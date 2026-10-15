"""Is the Python copy of the prompt still the app's prompt?

Runs the app's own JavaScript (``functions/memoirOutline.js``) with Node on every case and
compares, word for word: the cleaned request, the prompt, and the clean-up of sample answers.
Needs the app's source on this computer; free (no model calls).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .fixtures import load_cases
from .prompt import MODEL_LABELS, build_draft_prompt, clean_draft, clean_request, client_body
from .run import EXAMPLES_DIR

NODE_SCRIPT = r"""
const m = require(process.argv[1]);
const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const out = jobs.map((j) => {
  const r = m.cleanOutlineRequest(j.body);
  return { r, prompt: m.buildDraftPrompt(r), cleaned: j.answers.map((a) => m.cleanDraft(a, r)) };
});
process.stdout.write(JSON.stringify(out));
"""


def run_parity(app_dir: Path) -> tuple[bool, list[str]]:
    module = app_dir / "functions" / "memoirOutline.js"
    if not module.exists():
        return False, [f"Can't find {module}. Point --app at the Kairos app's folder."]
    if not shutil.which("node"):
        return False, ["Node isn't installed, so the app's JavaScript can't run here."]
    answers = [json.loads(p.read_text())["answer"] for p in sorted((EXAMPLES_DIR / "planted").glob("*.json"))
               if "answer" in json.loads(p.read_text())]
    answers += [json.loads(p.read_text()) for p in sorted((EXAMPLES_DIR / "reference").glob("*.json"))]
    answers += [{"bookType": "resilience", "chapters": [{"keep": "price-out-loud"}, {"title": "  padded  ", "entryIds": ["rv01", 7, None]}, "junk"]}, {}, []]
    jobs = []
    for case in load_cases():
        for model in MODEL_LABELS:
            jobs.append({"case": case.id, "model": model, "body": client_body(dict(case.settings), case.memoir, model), "answers": answers})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(jobs, f, ensure_ascii=False)
        tmp = f.name
    try:
        done = subprocess.run(["node", "-e", NODE_SCRIPT, str(module), tmp], capture_output=True, text=True, timeout=120)
    finally:
        Path(tmp).unlink(missing_ok=True)
    if done.returncode != 0:
        return False, [f"The app's JavaScript failed: {done.stderr.strip()[:400]}"]
    results = json.loads(done.stdout)
    notes, ok = [], True
    for job, js in zip(jobs, results):
        r = clean_request(job["body"])
        where = f"{job['case']} on {job['model']}"
        if r != js["r"]:
            ok = False
            notes.append(f"{where}: the cleaned request differs")
        if build_draft_prompt(r) != js["prompt"]:
            ok = False
            notes.append(f"{where}: the prompt differs")
        for n, (a, cleaned) in enumerate(zip(job["answers"], js["cleaned"])):
            if clean_draft(a, r) != cleaned:
                ok = False
                notes.append(f"{where}: clean-up of sample answer {n + 1} differs")
    notes.append(f"Compared {len(jobs)} prompts and {len(jobs) * len(answers)} answer clean-ups with the app's own code.")
    return ok, notes
