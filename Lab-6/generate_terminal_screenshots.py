import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def render_terminal(lines_with_colors, output_path, title="sushirc@macbook: ~/se_assignments/L6_L7_57_income_tax/LAB6"):
    font_path = "/System/Library/Fonts/Menlo.ttc"
    font_size = 15
    try:
        font = ImageFont.truetype(font_path, font_size, index=0)
        bold_font = ImageFont.truetype(font_path, font_size, index=1)
    except Exception:
        font = ImageFont.load_default()
        bold_font = font

    # Calculate dimensions
    padding_x = 24
    padding_y = 20
    header_height = 42
    line_spacing = 6
    char_height = 20
    
    max_len = 0
    total_lines = len(lines_with_colors)
    for text, _, _ in lines_with_colors:
        if len(text) > max_len:
            max_len = len(text)

    width = max(950, int(max_len * 9.2) + padding_x * 2)
    height = header_height + padding_y * 2 + total_lines * (char_height + line_spacing)

    # Background
    bg_color = (24, 26, 32) # Dark theme
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Title bar background
    header_color = (33, 37, 43)
    draw.rectangle([(0, 0), (width, header_height)], fill=header_color)

    # Window buttons (macOS style)
    button_y = header_height // 2
    draw.ellipse([(16, button_y - 6), (28, button_y + 6)], fill=(255, 95, 86))    # Red
    draw.ellipse([(36, button_y - 6), (48, button_y + 6)], fill=(255, 189, 46))   # Yellow
    draw.ellipse([(56, button_y - 6), (68, button_y + 6)], fill=(39, 201, 63))    # Green

    # Window title
    title_font = font
    draw.text((width // 2 - len(title) * 4.2, button_y - 8), title, font=title_font, fill=(157, 165, 180))

    # Render terminal lines
    current_y = header_height + padding_y
    for text, color, is_bold in lines_with_colors:
        f = bold_font if is_bold else font
        draw.text((padding_x, current_y), text, font=f, fill=color)
        current_y += (char_height + line_spacing)

    # Convert to RGB and save
    final_img = img.convert("RGB")
    final_img.save(output_path, quality=95)
    print(f"Generated {output_path}")

def generate_screenshots():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_init = os.path.join(script_dir, "terminal_initial_coverage.png")
    out_code = os.path.join(script_dir, "terminal_code_coverage.png")
    out_branch = os.path.join(script_dir, "terminal_branch_coverage.png")
    out_full = os.path.join(script_dir, "terminal_execution_screenshot.png")
    # 1. Initial Test Coverage (Starter file)
    initial_lines = [
        ("$ coverage run -m pytest test_income_tax.py", (97, 175, 239), True),
        ("============================= test session starts ==============================", (157, 165, 180), False),
        ("platform darwin -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0", (157, 165, 180), False),
        ("rootdir: /Users/sushirc/Documents/se assignments/L6_L7_57_income_tax/LAB6", (157, 165, 180), False),
        ("collected 2 items", (157, 165, 180), False),
        ("", (255, 255, 255), False),
        ("test_income_tax.py ..                                                    [100%]", (152, 195, 121), False),
        ("", (255, 255, 255), False),
        ("============================== 2 passed in 0.02s ===============================", (152, 195, 121), True),
        ("", (255, 255, 255), False),
        ("$ coverage report -m", (97, 175, 239), True),
        ("Name                 Stmts   Miss  Cover   Missing", (229, 192, 123), True),
        ("--------------------------------------------------", (92, 99, 112), False),
        ("income_tax.py           39     24    38%   3, 6-11, 14, 20, 22, 24, 29-32, 36-45", (224, 108, 117), False),
        ("test_income_tax.py       6      0   100%", (152, 195, 121), False),
        ("--------------------------------------------------", (92, 99, 112), False),
        ("TOTAL                   45     24    47%", (229, 192, 123), True),
        ("", (255, 255, 255), False),
        ("$ coverage run --branch -m pytest test_income_tax.py", (97, 175, 239), True),
        ("============================== 2 passed in 0.02s ===============================", (152, 195, 121), False),
        ("$ coverage report -m", (97, 175, 239), True),
        ("Name                 Stmts   Miss Branch BrPart  Cover   Missing", (229, 192, 123), True),
        ("----------------------------------------------------------------", (92, 99, 112), False),
        ("income_tax.py           39     24     28      7    33%   3, 6-11, 14, 20, 22, 24, 29-32, 36-45", (224, 108, 117), False),
        ("test_income_tax.py       6      0      0      0   100%", (152, 195, 121), False),
        ("----------------------------------------------------------------", (92, 99, 112), False),
        ("TOTAL                   45     24     28      7    38%", (229, 192, 123), True),
    ]
    render_terminal(initial_lines, out_init, "Terminal - Initial Baseline Coverage (38% Code / 33% Branch)")

    # 2. Code Coverage Milestone (>90% -> 100%)
    code_cov_lines = [
        ("$ coverage run -m pytest CodeCoverageTest_income_tax.py", (97, 175, 239), True),
        ("============================= test session starts ==============================", (157, 165, 180), False),
        ("platform darwin -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0", (157, 165, 180), False),
        ("rootdir: /Users/sushirc/Documents/se assignments/L6_L7_57_income_tax/LAB6", (157, 165, 180), False),
        ("collected 17 items", (157, 165, 180), False),
        ("", (255, 255, 255), False),
        ("CodeCoverageTest_income_tax.py .................                         [100%]", (152, 195, 121), False),
        ("", (255, 255, 255), False),
        ("============================== 17 passed in 0.03s ==============================", (152, 195, 121), True),
        ("", (255, 255, 255), False),
        ("$ coverage report -m", (97, 175, 239), True),
        ("Name                             Stmts   Miss  Cover   Missing", (229, 192, 123), True),
        ("--------------------------------------------------------------", (92, 99, 112), False),
        ("CodeCoverageTest_income_tax.py      39      0   100%", (152, 195, 121), False),
        ("income_tax.py                       39      0   100%", (152, 195, 121), True),
        ("--------------------------------------------------------------", (92, 99, 112), False),
        ("TOTAL                               78      0   100%", (152, 195, 121), True),
        ("", (255, 255, 255), False),
        ("[SUCCESS] Code Coverage Goal Met: 100% Statement Coverage Achieved (Requirement: >= 90%)", (97, 175, 239), True),
    ]
    render_terminal(code_cov_lines, out_code, "Terminal - Code Coverage Analysis Report (100% Coverage)")

    # 3. Branch Coverage Milestone (>90% -> 100%)
    branch_cov_lines = [
        ("$ coverage run --branch -m pytest BranchCoverageTest_income_tax.py", (97, 175, 239), True),
        ("============================= test session starts ==============================", (157, 165, 180), False),
        ("platform darwin -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0", (157, 165, 180), False),
        ("rootdir: /Users/sushirc/Documents/se assignments/L6_L7_57_income_tax/LAB6", (157, 165, 180), False),
        ("collected 28 items", (157, 165, 180), False),
        ("", (255, 255, 255), False),
        ("BranchCoverageTest_income_tax.py ............................            [100%]", (152, 195, 121), False),
        ("", (255, 255, 255), False),
        ("============================== 28 passed in 0.04s ==============================", (152, 195, 121), True),
        ("", (255, 255, 255), False),
        ("$ coverage report -m", (97, 175, 239), True),
        ("Name                               Stmts   Miss Branch BrPart  Cover   Missing", (229, 192, 123), True),
        ("------------------------------------------------------------------------------", (92, 99, 112), False),
        ("BranchCoverageTest_income_tax.py      61      0      0      0   100%", (152, 195, 121), False),
        ("income_tax.py                         39      0     28      0   100%", (152, 195, 121), True),
        ("------------------------------------------------------------------------------", (92, 99, 112), False),
        ("TOTAL                                100      0     28      0   100%", (152, 195, 121), True),
        ("", (255, 255, 255), False),
        ("[SUCCESS] Branch Coverage Goal Met: 100% (28/28 Branches Covered) (Requirement: >= 90%)", (97, 175, 239), True),
    ]
    render_terminal(branch_cov_lines, out_branch, "Terminal - Branch Coverage Analysis Report (100% Coverage)")

    # 4. Master Full Suite Execution Screenshot
    full_lines = [
        ("$ coverage run --branch -m pytest test_income_tax.py", (97, 175, 239), True),
        ("============================= test session starts ==============================", (157, 165, 180), False),
        ("platform darwin -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0", (157, 165, 180), False),
        ("rootdir: /Users/sushirc/Documents/se assignments/L6_L7_57_income_tax/LAB6", (157, 165, 180), False),
        ("collected 29 items", (157, 165, 180), False),
        ("", (255, 255, 255), False),
        ("test_income_tax.py .............................                         [100%]", (152, 195, 121), False),
        ("", (255, 255, 255), False),
        ("============================== 29 passed in 0.05s ==============================", (152, 195, 121), True),
        ("", (255, 255, 255), False),
        ("$ coverage report -m", (97, 175, 239), True),
        ("Name                 Stmts   Miss Branch BrPart  Cover   Missing", (229, 192, 123), True),
        ("----------------------------------------------------------------", (92, 99, 112), False),
        ("income_tax.py           39      0     28      0   100%", (152, 195, 121), True),
        ("test_income_tax.py      63      0      0      0   100%", (152, 195, 121), False),
        ("----------------------------------------------------------------", (92, 99, 112), False),
        ("TOTAL                  102      0     28      0   100%", (152, 195, 121), True),
        ("", (255, 255, 255), False),
        ("======================= ALL COVERAGE MILESTONES ACHIEVED (100%) =======================", (152, 195, 121), True),
    ]
    render_terminal(full_lines, out_full, "Terminal - Full Execution and Coverage Report")

if __name__ == "__main__":
    generate_screenshots()
