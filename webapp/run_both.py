"""
Launches both demo sites at once (Nimbus Bank on :5000, Pixel Outfitters
on :5001) in a single process, using separate threads for each Flask app.

This is purely a local convenience for the classroom -- for anything real
you'd run each site as its own process (see the Dockerfile / compose.yaml).
"""

import threading

from app import SITES, create_app


def run_site(site_key: str):
    app = create_app(site_key)
    app.run(port=SITES[site_key]["port"], debug=False, use_reloader=False)


def main():
    threads = [
        threading.Thread(target=run_site, args=(key,), daemon=True)
        for key in SITES
    ]
    for t in threads:
        t.start()

    print("Both demo sites are running:")
    for key, site in SITES.items():
        print(f"  {site['name']:<20} http://localhost:{site['port']}")
    print("\nPress Ctrl+C to stop.")

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nbye!")


if __name__ == "__main__":
    main()
