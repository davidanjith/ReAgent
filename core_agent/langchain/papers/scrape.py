import json
import os
import requests


def download_pdfs_from_json(json_path, output_dir='.'):
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        papers = json.load(f)

    flattened = {k: v for d in papers for k, v in d.items()}

    for title, url in flattened.items():
        try:
            print(f"Downloading: {title}")
            response = requests.get(url)
            response.raise_for_status()

            safe_title = title.replace(' ', '_') + '.pdf'
            output_path = os.path.join(output_dir, safe_title)

            with open(output_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Saved to: {output_path}")
        except Exception as e:
            print(f"Failed to download {title}: {e}")


# Example usage
download_pdfs_from_json('links.json')
