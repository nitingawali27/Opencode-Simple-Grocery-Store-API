"""
publish_results.py - Publish pytest results to Azure Test Plans via REST API

This script:
1. Reads JUnit XML output from pytest
2. Creates a test run in Azure DevOps linked to your Test Plan
3. Uploads each test result to that run
4. Marks the run as Completed

Required environment variables (set automatically by Azure Pipelines):
  SYSTEM_ACCESSTOKEN              - OAuth token (needs "Allow scripts to access OAuth token")
  SYSTEM_TEAMFOUNDATIONCOLLECTIONURI - e.g. https://dev.azure.com/yourorg/
  SYSTEM_TEAMPROJECT              - e.g. MyProject
  BUILD_BUILDID                   - current pipeline build ID

Optional environment variables (set as pipeline variables):
  TEST_PLAN_ID                    - Azure Test Plan ID to link this run to
  JUNIT_XML_PATH                  - path to JUnit XML file (default: results_testplan.xml)
  TEST_RUN_TITLE                  - name shown in Test Plans (default: Automated Pytest Run)
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
        print(f"[ERROR] Required environment variable '{name}' is not set.")
        sys.exit(1)
    return value


def ado_request(url, method, body=None, token=None):
    """Make an Azure DevOps REST API request."""
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
        error_body = e.read().decode('utf-8')
        print(f"[ERROR] HTTP {e.code} calling {method} {url}")
        print(f"        {error_body}")
        raise


# ---------------------------------------------------------------------------
# JUnit XML parser
# ---------------------------------------------------------------------------

def parse_junit(xml_path):
    """Return list of dicts with keys: name, outcome, duration_ms, error_message."""
    if not os.path.exists(xml_path):
        print(f"[ERROR] JUnit XML not found at: {xml_path}")
        sys.exit(1)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Support both <testsuites><testsuite> and bare <testsuite>
    suites = root.findall('.//testsuite')
    if not suites:
        suites = [root]

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
                outcome = 'Failed'
                message = (failure.get('message') or failure.text or '').strip()
            elif error is not None:
                outcome = 'Failed'
                message = (error.get('message') or error.text or '').strip()
            elif skipped is not None:
                outcome = 'NotApplicable'
                message = (skipped.get('message') or '').strip()
            else:
                outcome = 'Passed'
                message = ''

            results.append({
                'name': full_name,
                'outcome': outcome,
                'duration_ms': duration_ms,
                'error_message': message,
            })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # --- Read environment ---
    token        = env('SYSTEM_ACCESSTOKEN')
    org_url      = env('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI').rstrip('/')
    project      = env('SYSTEM_TEAMPROJECT')
    build_id     = env('BUILD_BUILDID')
    xml_path     = env('JUNIT_XML_PATH', required=False, default='results_testplan.xml')
    plan_id_str  = env('TEST_PLAN_ID',   required=False)
    run_title    = env('TEST_RUN_TITLE', required=False, default='Automated Pytest Run')

    api_base = f"{org_url}/{project}/_apis/test"
    api_ver  = 'api-version=7.1'

    # --- Parse JUnit XML ---
    print(f"[INFO] Parsing results from: {xml_path}")
    results = parse_junit(xml_path)
    total   = len(results)
    passed  = sum(1 for r in results if r['outcome'] == 'Passed')
    failed  = sum(1 for r in results if r['outcome'] == 'Failed')
    print(f"[INFO] Found {total} tests  |  Passed: {passed}  |  Failed: {failed}")

    # --- Create test run ---
    run_body = {
        "name": run_title,
        "isAutomated": True,
        "state": "InProgress",
        "buildId": build_id,
        "startedDate": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    if plan_id_str and plan_id_str.strip().lstrip('-').isdigit():
        run_body["plan"] = {"id": int(plan_id_str)}
        print(f"[INFO] Linking run to Test Plan ID: {plan_id_str}")
    elif plan_id_str:
        print(f"[WARN] TEST_PLAN_ID '{plan_id_str}' is not a valid number — skipping plan link.")

    print(f"[INFO] Creating test run '{run_title}' ...")
    run = ado_request(f"{api_base}/runs?{api_ver}", 'POST', run_body, token)
    run_id = run['id']
    print(f"[INFO] Test run created  ->  ID: {run_id}")

    # --- Upload results (max 1000 per request) ---
    batch_size = 200
    result_payloads = [
        {
            "testCaseTitle": r['name'],
            "automatedTestName": r['name'],
            "automatedTestType": "pytest",
            "outcome": r['outcome'],
            "durationInMs": r['duration_ms'],
            "errorMessage": r['error_message'],
            "state": "Completed",
            "completedDate": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        for r in results
    ]

    for i in range(0, len(result_payloads), batch_size):
        batch = result_payloads[i:i + batch_size]
        print(f"[INFO] Uploading results {i + 1}–{i + len(batch)} of {total} ...")
        ado_request(f"{api_base}/runs/{run_id}/results?{api_ver}", 'POST', batch, token)

    # --- Complete the run ---
    complete_body = {
        "state": "Completed",
        "completedDate": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    ado_request(f"{api_base}/runs/{run_id}?{api_ver}", 'PATCH', complete_body, token)
    print(f"[INFO] Test run {run_id} marked as Completed.")
    print(f"[INFO] View run at: {org_url}/{project}/_TestManagement/Runs?runId={run_id}")


if __name__ == '__main__':
    main()
