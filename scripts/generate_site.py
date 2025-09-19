import os
import requests
import json
from datetime import datetime
import base64
from html import escape

REPO_OWNER = os.environ.get('GITHUB_REPOSITORY_OWNER', 'ExistingPerson08')
REPO_NAME = os.environ.get('GITHUB_REPOSITORY_NAME', 'homebrew-tap')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

SITE_NAME = "Glowing Brew"
PAGE_DESCRIPTION = "Repository (tap) with Homebrew packages."
INTRO_TEXT = """
    <p>Glowing brew is a homebrew tap inspired by <a href="https://aur.archlinux.org" target="_blank">Aur</a>. It (will) contains my favorite apps, my projects and packages for <a href="https://github.com/ExistingPerson08/Spacefin" target="_blank">Spacefin</a>.
    It should support both Linux and MacOS, but only Linux is tested and supported. To add this tap, run this command in your terminal:</p>
    <div class="code-block-wrapper">
        <pre><code>brew tap existingperson08/tap</code></pre>
        <button>Copy</button>
    </div>
"""

PACKAGE_DIRS = ['Formula', 'Casks']
LIST_LIMIT = 5
OUTPUT_DIR = 'dist'

def make_api_request(url):
    """Odešle požadavek na GitHub API s autorizací."""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    return response.json()

def parse_date(date_str):
    """Převede ISO 8601 datum na český formát."""
    return datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%d. %m. %Y')

def get_description_from_content(content):
    """Získá popis balíčku z obsahu souboru."""
    for line in content.splitlines():
        # Hledáme řádek obsahující 'desc "'
        if 'desc "' in line:
            # Zajistí, že vezme text mezi uvozovkami
            try:
                return line.split('desc "')[1].split('"')[0]
            except IndexError:
                continue
    return 'Description was not found.'

# --- HTML ŠABLONY ---
def get_base_template(title, content):
    return f"""
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        body { overflow-y: scroll; }
        :root {{ --color-slate-900: #0f172a; --color-slate-800: #1e293b; --color-slate-700: #334155; --color-slate-500: #64748b; --color-slate-400: #94a3b8; --color-slate-300: #cbd5e1; --color-white: #ffffff; --color-sky-400: #38bdf8; --color-sky-500: #0ea5e9; --color-blue-900: #1e3a8a; --color-red-700: #b91c1c; --color-red-900: #450a0a; }} @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }} html {{ background-color: var(--color-slate-900); scroll-behavior: smooth; }} body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: var(--color-slate-300); margin: 0; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }} .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }} .background-gradient {{ position: absolute; top: 0; left: 0; width: 100%; height: 450px; background-image: linear-gradient(to bottom, var(--color-blue-900), var(--color-slate-900)); opacity: 0.6; z-index: -1; }} .main-content {{ position: relative; z-index: 1; animation: fadeIn 0.5s ease-out forwards; }} header {{ text-align: center; margin-bottom: 3rem; }} header h1 {{ font-size: 2.5rem; font-weight: 700; color: var(--color-white); letter-spacing: -0.025em; }} header a {{ color: inherit; text-decoration: none; }} header p {{ font-size: 1.125rem; color: var(--color-slate-400); margin-top: 0.5rem; max-width: 42rem; margin-left: auto; margin-right: auto; }} .prose {{ color: var(--color-slate-400); font-size: 1.125rem; line-height: 1.75; text-align: center; max-width: 45rem; margin: 0 auto 3rem auto; }} .prose p {{ margin-bottom: 1rem; }} .prose a {{ color: var(--color-sky-400); font-weight: 500; text-decoration: none; transition: color 0.2s; }} .prose a:hover {{ color: var(--color-sky-300); }} .prose pre {{ background-color: rgba(15, 23, 42, 0.7); border: 1px solid var(--color-slate-700); border-radius: 0.5rem; padding: 1rem; margin-top: 1rem; font-size: 0.875rem; white-space: pre-wrap; text-align: left; }} .grid-layout {{ display: grid; grid-template-columns: 1fr; gap: 2rem; }} @media (min-width: 1024px) {{ .grid-layout {{ grid-template-columns: 2fr 1fr; }} }} h2 {{ font-size: 1.75rem; font-weight: 700; color: var(--color-white); margin-bottom: 1rem; }} .search-box {{ position: relative; margin-bottom: 1.5rem; }} .search-box input {{ width: 100%; padding: 0.75rem 1rem 0.75rem 2.5rem; border: 1px solid var(--color-slate-700); border-radius: 0.5rem; background-color: rgba(30, 41, 59, 0.5); color: var(--color-slate-300); transition: all 0.2s; box-sizing: border-box; }} .search-box input:focus {{ outline: none; border-color: var(--color-sky-500); box-shadow: 0 0 0 2px var(--color-sky-500); }} .search-box svg {{ position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 1.25rem; height: 1.25rem; color: var(--color-slate-500); }} .package-card {{ display: block; padding: 1.25rem; background-color: rgba(30, 41, 59, 0.5); border: 1px solid var(--color-slate-700); border-radius: 0.75rem; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); text-decoration: none; margin-bottom: 1rem; }} .package-card:hover {{ transform: scale(1.02); border-color: rgba(56, 189, 248, 0.5); }} .package-card-header {{ display: flex; justify-content: space-between; align-items: flex-start; }} .package-card h3 {{ font-weight: 600; color: var(--color-sky-400); margin: 0; }} .package-card-date {{ font-size: 0.75rem; color: var(--color-slate-500); }} .package-card p {{ font-size: 0.875rem; color: var(--color-slate-400); margin: 0.25rem 0 0 0; }} .sidebar-card {{ background-color: rgba(30, 41, 59, 0.5); border: 1px solid var(--color-slate-700); border-radius: 0.75rem; padding: 1.25rem; backdrop-filter: blur(10px); }} .sidebar-card ul {{ list-style: none; padding: 0; margin: 0; }} .sidebar-card li:not(:last-child) {{ margin-bottom: 0.75rem; }} .sidebar-card a {{ font-weight: 600; color: var(--color-slate-300); text-decoration: none; transition: color 0.2s; }} .sidebar-card a:hover {{ color: var(--color-sky-400); }} .sidebar-card span {{ display: block; font-size: 0.875rem; color: var(--color-slate-500); }} .loader, .empty-state, .error-state {{ text-align: center; padding: 2rem; color: var(--color-slate-500); }} .error-state {{ background-color: var(--color-red-900); border: 1px solid var(--color-red-700); border-radius: 0.5rem; }} footer {{ margin-top: 3rem; text-align: center; font-size: 0.875rem; color: var(--color-slate-500); border-top: 1px solid var(--color-slate-800); padding-top: 1.5rem; }} .detail-card {{ background-color: rgba(30, 41, 59, 0.5); border: 1px solid var(--color-slate-700); border-radius: 0.75rem; padding: 1.5rem; backdrop-filter: blur(10px); }} .back-link {{ display: inline-flex; align-items: center; gap: 0.5rem; color: var(--color-sky-400); text-decoration: none; margin-bottom: 1.5rem; transition: color 0.2s; }} .back-link:hover {{ color: var(--color-sky-300); }} .back-link svg {{ transition: transform 0.2s; }} .back-link:hover svg {{ transform: translateX(-4px); }} .detail-card h2 {{ font-size: 2rem; }} .code-block-wrapper {{ position: relative; margin-top: 0.5rem; }} .code-block-wrapper pre {{ margin: 0; }} .code-block-wrapper button {{ position: absolute; top: 0.75rem; right: 0.75rem; background-color: var(--color-slate-700); color: var(--color-slate-300); border: 1px solid var(--color-slate-500); border-radius: 0.375rem; padding: 0.25rem 0.5rem; font-size: 0.75rem; cursor: pointer; opacity: 0.5; transition: all 0.2s; }} .code-block-wrapper:hover button {{ opacity: 1; }} .code-block-wrapper button:hover {{ background-color: var(--color-slate-600); }} pre code.hljs {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; font-size: 0.875rem; line-height: 1.6; padding: 1rem !important; background-color: var(--color-slate-900) !important; border: 1px solid var(--color-slate-700); border-radius: 0.5rem; }} .tabs {{ border-bottom: 1px solid var(--color-slate-700); margin-top: 2rem; }} .tabs nav {{ display: flex; gap: 1.5rem; margin-bottom: -1px; }} .tabs button {{ background: none; border: none; color: var(--color-slate-400); padding: 1rem 0.25rem; font-size: 0.875rem; font-weight: 500; border-bottom: 2px solid transparent; cursor: pointer; transition: all 0.2s; }} .tabs button:hover {{ color: var(--color-slate-300); }} .tabs button.active {{ color: var(--color-sky-400); border-bottom-color: var(--color-sky-500); }} .tab-content {{ margin-top: 1.5rem; }} .history-list {{ list-style: none; padding: 0; margin: 0; }} .history-item {{ display: flex; gap: 0.99rem; position: relative; padding-bottom: 0.5rem; }} .history-item:not(:last-child)::before {{ content: ''; position: absolute; top: 1rem; left: 0.875rem; width: 2px; height: 100%; background-color: var(--color-slate-700); }} .history-icon {{ flex-shrink: 0; width: 2rem; height: 2rem; border-radius: 9999px; background-color: var(--color-slate-800); display: flex; align-items: center; justify-content: center; ring: 8px; box-shadow: 0 0 0 8px var(--color-slate-900); z-index: 1; }} .history-icon svg {{ width: 1.25rem; height: 1.25rem; color: var(--color-slate-400); }} .history-details {{ flex-grow: 1; padding-top: 0.25rem; }} .history-message {{ font-size: 0.875rem; font-weight: 500; color: var(--color-white); }} .history-message a {{ color: inherit; text-decoration: none; }} .history-message a:hover {{ text-decoration: underline; }} .history-author {{ font-size: 0.875rem; color: var(--color-slate-500); }} .history-date {{ font-size: 0.875rem; color: var(--color-slate-500); text-align: right; }}
    </style>
</head>
<body>
    <div class="background-gradient"></div>
    <div class="container">
        <div class="main-content">
            <header>
                <h1><a href="https://github.com/ExistingPerson08/homebrew-tap/">{escape(SITE_NAME)}</a></h1>
                <p>{escape(PAGE_DESCRIPTION)}</p>
            </header>
            <main>{content}</main>
            <footer>Site generated using Python and Github Actions.</footer>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // Zvýraznění syntaxe
            if (typeof hljs !== 'undefined') {{
                hljs.highlightAll();
            }}

            // Funkce pro kopírování
            document.body.addEventListener('click', e => {{
                if (e.target.matches('.code-block-wrapper button')) {{
                    const code = e.target.previousElementSibling.querySelector('code').innerText;
                    navigator.clipboard.writeText(code).then(() => {{
                        e.target.innerText = 'Zkopírováno!';
                        setTimeout(() => {{ e.target.innerText = 'Kopírovat'; }}, 2000);
                    }});
                }}
            }});
            
            // Přepínání tabů na detailní stránce
            const tabs = document.querySelectorAll('.tabs button');
            if (tabs.length > 0) {{
                tabs.forEach(button => button.addEventListener('click', () => {{
                    const tabId = button.dataset.tab;
                    tabs.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    document.querySelectorAll('.tab-content').forEach(content => {{
                        // ZMĚNA: oprava selektoru pro obsah tabu
                        content.style.display = content.id === `tab-${{tabId}}` ? 'block' : 'none';
                    }});
                }}));
                // Aktivace prvního tabu
                if(document.getElementById('tab-details')) {{
                   document.getElementById('tab-details').style.display = 'block';
                }}
            }}

            // Vyhledávání na hlavní stránce
            const searchInput = document.getElementById('search-input');
            if (searchInput) {{
                searchInput.addEventListener('input', (e) => {{
                    const query = e.target.value.toLowerCase().trim();
                    const packages = document.querySelectorAll('.package-card');
                    let visibleCount = 0;
                    packages.forEach(pkg => {{
                        const textContent = pkg.dataset.searchContent || pkg.textContent.toLowerCase();
                        if (textContent.toLowerCase().includes(query)) {{
                            pkg.style.display = 'block';
                            visibleCount++;
                        }} else {{
                            pkg.style.display = 'none';
                        }}
                    }});
                    const emptyState = document.getElementById('empty-state');
                    if(emptyState) emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
                }});
            }}
        }});
    </script>
</body>
</html>
"""

def get_home_page_content(packages, recently_updated, recently_added):
    package_list_html = "".join([
        f"""<a href="./packages/{escape(pkg['name'])}.html" class="package-card" data-search-content="{escape(pkg['name'])} {escape(pkg['description'])} {escape(pkg['last_update'])}">
            <div class="package-card-header">
                <h3>{escape(pkg['name'])}</h3>
                <span class="package-card-date">{escape(pkg['last_update'])}</span>
            </div>
            <p>{escape(pkg['description'])}</p>
        </a>"""
        for pkg in sorted(packages, key=lambda p: p['name'])
    ])
    
    updated_list_html = "".join([
        f'<li><a href="./packages/{escape(p["name"])}.html">{escape(p["name"])}</a><span>{escape(p["date"])}</span></li>'
        for p in recently_updated
    ]) or '<li><span style="color:var(--color-slate-500)">Žádné položky.</span></li>'

    added_list_html = "".join([
        f'<li><a href="./packages/{escape(p["name"])}.html">{escape(p["name"])}</a><span>{escape(p["date"])}</span></li>'
        for p in recently_added
    ]) or '<li><span style="color:var(--color-slate-500)">Žádné položky.</span></li>'

    return f"""
        <div class="prose">{INTRO_TEXT}</div>
        <div class="grid-layout">
            <div>
                <h2>All packages</h2>
                <div class="search-box">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    <input type="search" id="search-input" placeholder="Search in name, description, date...">
                </div>
                <div id="packages-output">{package_list_html}</div>
                <div id="empty-state" class="empty-state" style="display: none;">No packages found.</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 2rem;">
                <div class="sidebar-card"><h2>Recently updated</h2><ul>{updated_list_html}</ul></div>
                <div class="sidebar-card"><h2>Recently added</h2><ul>{added_list_html}</ul></div>
            </div>
        </div>
    """

def get_detail_page_content(pkg):
    history_html = "".join([
        f"""<li class="history-item">
            <div class="history-icon"><svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z" clip-rule="evenodd" /></svg></div>
            <div style="display: flex; justify-content: space-between; flex-grow: 1;">
                <div class="history-details">
                    <p class="history-message"><a href="{escape(c['url'])}" target="_blank">{escape(c['message'])}</a></p>
                    <p class="history-author">od {escape(c['author'])}</p>
                </div>
                <time class="history-date">{escape(c['date'])}</time>
            </div>
        </li>"""
        for c in pkg['history']
    ]) or '<div class="empty-state">No history.</div>'
    
    install_command = f"brew install {REPO_OWNER}/{REPO_NAME}/{pkg['name']}"
    if pkg['type'] == 'cask':
        install_command = f"brew install --cask {REPO_OWNER}/{REPO_NAME}/{pkg['name']}"

    return f"""
        <div style="max-width: 48rem; margin: 0 auto;">
            <a href="../" class="back-link">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                Back&nbsp;to list
            </a>
            <div class="detail-card">
                <h2>{escape(pkg['name'])}</h2>
                <p style="font-size: 1.125rem; color: var(--color-slate-400); margin-top: 0.25rem;">{escape(pkg['description'])}</p>
                <div style="margin-top: 1.5rem;">
                    <h3 style="font-weight: 600; color: var(--color-white);">Instalace:</h3>
                    <div class="code-block-wrapper"><pre><code>{escape(install_command)}</code></pre><button>Kopírovat</button></div>
                </div>
                <div class="tabs">
                    <nav>
                        <button class="active" data-tab="details">File content</button>
                        <button data-tab="history">Change history</button>
                    </nav>
                </div>
                <div id="tab-content-container">
                    <div id="tab-details" class="tab-content">
                        <div class="code-block-wrapper"><pre><code class="language-ruby">{escape(pkg['content'])}</code></pre><button>Kopírovat</button></div>
                    </div>
                    <div id="tab-history" class="tab-content" style="display: none;"><ul class="history-list">{history_html}</ul></div>
                </div>
            </div>
        </div>
    """

# --- HLAVNÍ LOGIKA SKRIPTU ---
def main():
    print("Spouštím generování stránky...")
    
    os.makedirs(os.path.join(OUTPUT_DIR, 'packages'), exist_ok=True)
    
    # ZMĚNA: Načítání balíčků z více adresářů
    packages = []
    print("Načítám seznam balíčků...")
    for dir_name in PACKAGE_DIRS:
        try:
            # Určení typu balíčku z názvu adresáře ('Formula' -> 'formula', 'Casks' -> 'cask')
            pkg_type = dir_name.lower().rstrip('s')
            print(f"  -> Prohledávám adresář '{dir_name}'...")
            files = make_api_request(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{dir_name}")
            
            for file in files:
                if file['type'] == 'file' and file['name'].endswith('.rb'):
                    packages.append({
                        "name": file['name'].replace('.rb', ''),
                        "path": file['path'],
                        "type": pkg_type,  # Přidání typu balíčku
                        "description": "Načítám...",
                        "last_update": "Neznámé"
                    })
        except requests.exceptions.HTTPError as e:
            # Pokud adresář neexistuje (např. v tapu nejsou žádné Casks), jen vypíšeme varování
            if e.response.status_code == 404:
                print(f"  -> Varování: Adresář '{dir_name}' nebyl nalezen. Přeskakuji.")
            else:
                raise e # Jinou chybu vyvoláme dál
    
    print("\nNačítám historii commitů pro zjištění změn...")
    # ZMĚNA: Získáváme commity pro celé repo, abychom pokryli všechny adresáře
    commits = make_api_request(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?per_page=100")
    
    package_events = {}
    
    # Procházíme commity od nejstaršího po nejnovější
    for commit in reversed(commits):
        commit_details = make_api_request(commit['url'])
        commit_date_str = commit_details['commit']['committer']['date']
        commit_date_obj = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
        
        for file in commit_details['files']:
            # ZMĚNA: Kontrolujeme, zda soubor patří do některého z našich adresářů
            if not (any(file['filename'].startswith(f"{d}/") for d in PACKAGE_DIRS) and file['filename'].endswith('.rb')):
                continue

            pkg_name = os.path.basename(file['filename']).replace('.rb', '')
            
            # Záznam data vytvoření
            if pkg_name not in package_events and file['status'] == 'added':
                package_events[pkg_name] = {
                    'name': pkg_name,
                    'created_at': commit_date_obj,
                    'updated_at': commit_date_obj,
                }
            # Aktualizace data poslední změny
            elif pkg_name in package_events:
                package_events[pkg_name]['updated_at'] = commit_date_obj

    # Aktualizujeme hlavní seznam balíčků
    for pkg in packages:
        if pkg['name'] in package_events:
            event_data = package_events[pkg['name']]
            pkg['last_update'] = event_data['updated_at'].strftime('%d. %m. %Y')

    # Sestavení finálních seznamů pro postranní panel
    all_added = sorted(package_events.values(), key=lambda p: p['created_at'], reverse=True)
    all_updated = sorted(
        [p for p in package_events.values() if p['created_at'] != p['updated_at']],
        key=lambda p: p['updated_at'], 
        reverse=True
    )

    recently_added = [{'name': p['name'], 'date': p['created_at'].strftime('%d. %m. %Y')} for p in all_added[:LIST_LIMIT]]
    recently_updated = [{'name': p['name'], 'date': p['updated_at'].strftime('%d. %m. %Y')} for p in all_updated[:LIST_LIMIT]]

    print(f"\nNalezeno {len(packages)} balíčků. Generuji detailní stránky...")
    for pkg in packages:
        try:
            content_data = make_api_request(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{pkg['path']}")
            decoded_content = base64.b64decode(content_data['content']).decode('utf-8')
            pkg['content'] = decoded_content
            
            if pkg['description'] == "Načítám...":
                pkg['description'] = get_description_from_content(decoded_content)

            history_data = make_api_request(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?path={pkg['path']}&per_page=10")
            pkg['history'] = [
                {
                    "message": c['commit']['message'],
                    "author": c['commit']['author']['name'],
                    "date": parse_date(c['commit']['author']['date']),
                    "url": c['html_url']
                } for c in history_data
            ]
            
            detail_content = get_detail_page_content(pkg)
            detail_html = get_base_template(f"{pkg['name']} | {SITE_NAME}", detail_content)
            
            with open(os.path.join(OUTPUT_DIR, 'packages', f"{pkg['name']}.html"), 'w', encoding='utf-8') as f:
                f.write(detail_html)
            print(f"  - Stránka pro '{pkg['name']}' ({pkg['type']}) vygenerována.")

        except Exception as e:
            print(f"  - CHYBA při generování stránky pro '{pkg['name']}': {e}")
            
    print("\nGeneruji hlavní stránku (index.html)...")
    home_content = get_home_page_content(packages, recently_updated, recently_added)
    home_html = get_base_template(SITE_NAME, home_content)
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(home_html)

    print("\nGenerování dokončeno!")
    print(f"Statické soubory jsou připraveny ve složce '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()
