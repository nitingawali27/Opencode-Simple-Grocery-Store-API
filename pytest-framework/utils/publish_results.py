"""
publish_results.py - Publish pytest results to Azure Test Plans via REST API

Strategy:
  1. Look for the most recent "NotStarted" OnDemandTestRun for the Test Plan.
  2. If found, UPDATE that run with pytest results so it shows Completed.
  3. If not found (e.g. pipeline triggered manually), CREATE a new linked run.

Required environment variables (set automatically by Azure Pipelines):
  SYSTEM_ACCESSTOKEN                 - OAuth token (enable "Allow scripts to access OAuth token")
  SYSTEM_TEAMFOUNDATIONCOLLECTIONURI - e.g. https://dev.azure.com/yourorg/
  SYSTEM_TEAMPROJECT                 - e.g. MyProject
  BUILD_BUILDID                      - current pipeline build ID

Optional pipeline variables:
  TEST_PLAN_ID    - Azure Test Plan ID (e.g. 1)
  JUNIT_XML_PATH  - path to JUnit XML (default: results_testplan.xml)
  TEST_RUN_TITLE  - fallback run name when creating a new run
"""

import os
import sys
import json
import base64
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def env(name, required=True, default=''):
    value = os.environ.get(name, default)
    if required and not value:
        print(f"[ERROR] Required env var '{name}' is not set.")
        sys.exit(1)
    return value


def is_valid_int(s):
    return bool(s) and s.strip().lstrip('-').isdigit()


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def ado_request(url, method, body=None, token=None):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    if token:
        credentials = base64.b64encode(f':{token}'.encode()).decode()
        headers['Authorization'] = f'Basic {credentials}'

    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}  {method}  {url}")
        print(f"        {e.read().decode('utf-8')}")
        raise


# ---------------------------------------------------------------------------
# JUnit XML parser
# ---------------------------------------------------------------------------

def parse_junit(xml_path):
    if not os.path.exists(xml_path):
        print(f"[ERROR] JUnit XML not found: {xml_path}")
        sys.exit(1)

    root = ET.parse(xml_path).getroot()
    suites = root.findall('.//testsuite') or [root]

    results = []
    for suite in suites:
        for tc in suite.findall('testcase'):
            classname = tc.get('classname', '')
            name = tc.get('name', 'unknown')
            full_name = f"{classname}.{name}" if classname else name
            duration_ms = int(float(tc.get('time', 0)) * 1000)

            failure = tc.find('failure')
            error   = tc.find('error')
            skipped = tc.find('skipped')

            if failure is not None:
                outcome, message = 'Failed', (failure.get('message') or failure.text or '').strip()
            elif error is not None:
                outcome, message = 'Failed', (error.get('message') or error.text or '').strip()
            elif skipped is not None:
                outcome, message = 'NotApplicable', (skipped.get('message') or '').strip()
            else:
                outcome, message = 'Passed', ''

            results.append({'name': full_name, 'outcome': outcome,
                            'duration_ms': duration_ms, 'error_message': message})
    return results


# ---------------------------------------------------------------------------
# Find existing OnDemandTestRun to update
# ---------------------------------------------------------------------------

def find_pending_run(api_base, plan_id, token):
    """
    Return the most recent NotStarted or InProgress test run for the plan,
    so we can update the run created by 'Run Automated Tests' instead of
    creating a new one (which leaves the OnDemandTestRun stuck at Not started).
    """
    try:
        url = f"{api_base}/runs?planId={plan_id}&api-version=7.1"
        resp = ado_request(url, 'GET', token=token)
        runs = resp.get('value', [])
        pending = [r for r in runs if r.get('state') in ('NotStarted', 'InProgress')]
        if pending:
            pending.sort(key=lambda r: r['id'], reverse=True)
            found = pending[0]
            print(f"[INFO] Found existing pending run ID {found['id']} ('{found['name']}') — will update it.")
            return found
    except Exception as exc:
        print(f"[WARN] Could not query existing runs: {exc}")
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    token     = env('SYSTEM_ACCESSTOKEN')
    org_url   = env('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI').rstrip('/')
    project   = env('SYSTEM_TEAMPROJECT')
    build_id  = env('BUILD_BUILDID')
    xml_path  = env('JUNIT_XML_PATH',  required=False, default='results_testplan.xml')
    plan_str  = env('TEST_PLAN_ID',    required=False)
    run_title = env('TEST_RUN_TITLE',  required=False, default='Automated Pytest Run')

    api_base = f"{org_url}/{project}/_apis/test"
    api_ver  = 'api-version=7.1'

    # Validate TEST_PLAN_ID
    plan_id = None
    if is_valid_int(plan_str):
        plan_id = int(plan_str)
        print(f"[INFO] Test Plan ID: {plan_id}")
    elif plan_str:
        print(f"[WARN] TEST_PLAN_ID '{plan_str}' is not a valid number — skipping plan link.")

    # --- Parse JUnit XML ---
    print(f"[INFO] Parsing: {xml_path}")
    results = parse_junit(xml_path)
    total  = len(results)
    passed = sum(1 for r in results if r['outcome'] == 'Passed')
    failed = sum(1 for r in results if r['outcome'] == 'Failed')
    print(f"[INFO] Tests: {total}  |  Passed: {passed}  |  Failed: {failed}")

    # --- Find the OnDemandTestRun OR create a new one ---
    run_id = None

    if plan_id:
        existing = find_pending_run(api_base, plan_id, token)
        if existing:
            run_id = existing['id']
            # Move it to InProgress so we can post results
            ado_request(f"{api_base}/runs/{run_id}?{api_ver}", 'PATCH',
                        {"state": "InProgress", "startedDate": now_iso()}, token)

    if run_id is None:
        print(f"[INFO] No pending OnDemandTestRun found — creating a new run.")
        body = {
            "name": run_title,
            "isAutomated": True,
            "state": "InProgress",
            "buildId": build_id,
            "startedDate": now_iso(),
        }
        if plan_id:
            body["plan"] = {"id": plan_id}
        run = ado_request(f"{api_base}/runs?{api_ver}", 'POST', body, token)
        run_id = run['id']
        print(f"[INFO] Created new test run ID: {run_id}")

    # --- Upload results in batches ---
    payloads = [
        {
            "testCaseTitle":    r['name'],
            "automatedTestName": r['name'],
            "automatedTestType": "pytest",
            "outcome":          r['outcome'],
            "durationInMs":     r['duration_ms'],
            "errorMessage":     r['error_message'],
            "state":            "Completed",
            "completedDate":    now_iso(),
        }
        for r in results
    ]

    batch_size = 200
    for i in range(0, len(payloads), batch_size):
        batch = payloads[i:i + batch_size]
        print(f"[INFO] Uploading results {i + 1}–{i + len(batch)} of {total} ...")
        ado_request(f"{api_base}/runs/{run_id}/results?{api_ver}", 'POST', batch, token)

    # --- Mark run Completed ---
    ado_request(f"{api_base}/runs/{run_id}?{api_ver}", 'PATCH',
                {"state": "Completed", "completedDate": now_iso()}, token)

    print(f"[INFO] Run {run_id} marked Completed.")
    print(f"[INFO] View at: {org_url}/{project}/_TestManagement/Runs?runId={run_id}")


if __name__ == '__main__':
    main()
