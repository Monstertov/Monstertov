#!/usr/bin/env python3
"""Render README.md and the images in img/ from tools/README.template.md in one color theme.

Switch: change THEME below and push. The workflow re-renders and commits.
Locally: python3 tools/theme.py [blue|white|mix]
"""
import base64
import pathlib
import sys
import textwrap
from html import escape
from urllib.parse import quote

THEME = "mix"

# heading: section headings, card titles, card icons, about labels
# text:    card text, about body text
THEMES = {
    "blue": {"heading": "0071bc", "text": "0071bc"},
    "white": {"heading": "ffffff", "text": "ffffff"},
    "mix": {"heading": "0071bc", "text": "ffffff"},
}

ABOUT = [
    ("", "Always trying to understand and keep learning. I dip my brain into a little bit of everything "
         "to get a better understanding of how everything works around me. System administrator by day "
         "and do whatever by night."),
    ("Favorite programming language:", "Visual Basic. It was the first thing I touched, and it broke my first computer."),
    ("Interests:", "Spaceflight, Geopolitics, Gaming and Computer Science."),
]

HEADINGS = {"readme": "README.md", "tech": "Technology stack", "active": "What I'm working on", "stats": "My stats"}

# One list per group: OS & cloud, software, tools, hardware. (name, link or None, logo, brand color). "feather:" logos come from feathericons.com, the rest from simpleicons.org.
TECH = [
    [("Debian", "https://www.debian.org/", "debian", "A81D33"),
     ("Ubuntu", "https://ubuntu.com/", "ubuntu", "E95420"),
     ("Arch Linux", "https://archlinux.org/", "arch-linux", "1793D1"),
     ("Kali Linux", "https://www.kali.org/", "kali-linux", "557C94"),
     ("Android", "https://www.android.com/", "android", "A4C639"),
     ("Windows Server", "https://www.microsoft.com/en-us/windows-server", "microsoft", "0078D6"),
     ("Microsoft Azure", "https://azure.microsoft.com/", "msazure", "0089D6")],
    [("Docker", "https://www.docker.com/", "docker", "2496ED"),
     ("MySQL", "https://www.mysql.com/", "mysql", "4479A1"),
     ("C++", "https://isocpp.org/", "cpp", "00599C"),
     ("Rust", "https://www.rust-lang.org/", "rust", "000000"),
     ("Python", "https://www.python.org/", "python", "3776AB"),
     ("JavaScript", "https://developer.mozilla.org/en-US/docs/Web/JavaScript", "javascript", "F7DF1E"),
     ("VB.NET", "https://learn.microsoft.com/en-us/dotnet/visual-basic/", "dotnet", "512BD4"),
     ("PHP", "https://www.php.net/", "php", "777BB4"),
     (".NET", "https://dotnet.microsoft.com/", "dotnet", "512BD4"),
     ("Bash", "https://www.gnu.org/software/bash/", "gnubash", "4EAA25"),
     ("PowerShell", "https://learn.microsoft.com/powershell/", "powershell", "012456"),
     ("jQuery", "https://jquery.com/", "jquery", "0769AD"),
     ("CSS", "https://developer.mozilla.org/en-US/docs/Web/CSS", "css3", "1572B6"),
     ("HTML", "https://developer.mozilla.org/en-US/docs/Web/HTML", "html5", "E34F26")],
    [("Git", "https://git-scm.com/", "git", "F05032"),
     ("3CX", "https://www.3cx.com/", "feather:phone", "0091C9"),
     ("Exim", "https://www.exim.org/", "feather:mail", "007ACC"),
     ("Wireshark", "https://www.wireshark.org/", "wireshark", "1679A7"),
     ("Nmap", "https://nmap.org/", "nmap", "00407A"),
     ("Tor", "https://www.torproject.org/", "torproject", "7E4798")],
    [("Arduino", "https://www.arduino.cc/", "arduino", "00969C"),
     ("Raspberry Pi", "https://www.raspberrypi.com/", "raspberrypi", "C51A4A"),
     ("HPE", "https://www.hpe.com/", "hp", "00B388")],
]

PROJECTS = [
    [("MSP Voice Portal", "https://github.com/Monstertov/msp-voice-portal", "feather:mic", "0071BC"),
     ("Python CLI Color Picker", "https://github.com/Monstertov/Python-Quick-Colorpicker", "feather:terminal", "007ACC"),
     ("Private Android App", None, "android", "A4C639"),
     ("Band Managing Webapp", None, "feather:music", "6441A5")],
]

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def badge(name, link, logo, brand):
    source = "&logoSource=feather" if logo.startswith("feather:") else ""
    label = quote(name.replace("-", "--").replace("_", "__"))
    r, g, b = (int(brand[i:i + 2], 16) for i in (0, 2, 4))
    fg = "black" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 200 else "white"  # dark logo on bright badges like JavaScript
    src = f"https://custom-icon-badges.demolab.com/badge/{label}-{brand}?logo={logo.removeprefix('feather:')}{source}&logoColor={fg}"
    img = f'<img src="{escape(src)}" alt="{escape(name)}" />'
    return f'  <a href="{escape(link)}" target="_blank">{img}</a>' if link else f"  {img}"


def badges(groups):
    return "\n  <br><br>\n".join("\n".join(badge(*b) for b in group) for group in groups)


def heading_svg(c, text, size=24):
    font = base64.b64encode((TOOLS / "fira-code.woff2").read_bytes()).decode()
    width = round(len(text) * 0.6 * size) + 4  # Fira Code advance width is 0.6 em
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{size + 16}">\n'
            f"<style>@font-face{{font-family:'Fira Code';font-weight:500;src:url(data:font/woff2;base64,{font}) format('woff2')}}</style>\n"
            f'<text x="2" y="{size + 4}" font-family="\'Fira Code\', monospace" font-weight="500" font-size="{size}" '
            f'fill="#{c["heading"]}">{escape(text)}</text>\n</svg>\n')


def about_svg(c, width=830, size=16, line=24, wrap=100):
    rows, y = [], size
    for label, body in ABOUT:
        for i, row in enumerate(textwrap.wrap(f"{label} {body}".strip(), wrap)):
            if i == 0 and label:
                row = f'<tspan font-weight="bold" fill="#{c["heading"]}">{escape(label)}</tspan>{escape(row[len(label):])}'
            else:
                row = escape(row)
            rows.append(f'  <text x="0" y="{y}">{row}</text>')
            y += line
        y += line // 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y - line}" font-family="{SANS}" '
            f'font-size="{size}" fill="#{c["text"]}">\n' + "\n".join(rows) + "\n</svg>\n")


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else THEME
    c = THEMES[name]
    readme = (TOOLS / "README.template.md").read_text()
    for key, value in {**c, "tech": badges(TECH), "projects": badges(PROJECTS)}.items():
        readme = readme.replace("{{" + key + "}}", value)
    assert "{{" not in readme, "unknown placeholder in tools/README.template.md"
    (ROOT / "README.md").write_text("<!-- Generated by tools/theme.py from tools/README.template.md. Edit those. -->\n" + readme)
    (ROOT / "img" / "about.svg").write_text(about_svg(c))
    for slug, text in HEADINGS.items():
        (ROOT / "img" / f"heading-{slug}.svg").write_text(heading_svg(c, text))
    print(f"rendered theme {name}")


if __name__ == "__main__":
    main()
