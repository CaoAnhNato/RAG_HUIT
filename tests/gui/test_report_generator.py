import json
import os

def generate_markdown_report(json_report_path, output_md_path):
    if not os.path.exists(json_report_path):
        print(f"JSON report not found at {json_report_path}")
        return

    with open(json_report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    summary = data.get("summary", {})
    tests = data.get("tests", [])

    md_content = "# Báo cáo GUI Test Chatbot RAG HUIT\n\n"
    
    md_content += f"## Tóm tắt\n"
    md_content += f"- **Tổng số test**: {summary.get('collected', 0)}\n"
    md_content += f"- **Passed**: {summary.get('passed', 0)}\n"
    md_content += f"- **Failed**: {summary.get('failed', 0)}\n"
    
    if summary.get('failed', 0) == 0 and summary.get('passed', 0) > 0:
        md_content += "- **Trạng thái**: ✅ Đạt 100% Passed\n"
    else:
        md_content += "- **Trạng thái**: ❌ Chưa đạt 100% Passed\n"

    md_content += "\n## Chi tiết kết quả\n"
    
    for test in tests:
        name = test.get("nodeid", "").split("::")[-1]
        outcome = test.get("outcome", "unknown")
        duration = test.get("call", {}).get("duration", 0) * 1000 # convert to ms
        
        status_icon = "✅" if outcome == "passed" else "❌"
        
        md_content += f"### {status_icon} {name}\n"
        md_content += f"- **Status**: {outcome.capitalize()}\n"
        md_content += f"- **Duration**: {duration:.2f} ms\n"
        
        if outcome == "failed":
            crash = test.get("call", {}).get("crash", {})
            md_content += f"**Error**: \n```\n{crash.get('message', 'Unknown Error')}\n```\n"
            
        md_content += "\n"

    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Report generated successfully at {output_md_path}")

if __name__ == "__main__":
    generate_markdown_report("gui_test_report.json", "GUI_Test_Report.md")
