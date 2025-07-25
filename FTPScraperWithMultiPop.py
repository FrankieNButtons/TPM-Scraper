#!/usr/bin/env python3
"""
**Description**
爬取 1000Genomes CEU 样本目录下每个一级子目录的 transcriptome 子目录中的 isoforms.results.tsv 文件，
并保存为 {子目录名称}.tsv。

**Usage**
    python FTPScraper.py [--output-dir OUTPUT_DIR]

**Params**
- `--output-dir`: 指定下载文件保存的本地目录，默认为当前目录下 `downloads/`。

"""

import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from get_user_agent import get_user_agent_of_pc
import threading
from tqdm import tqdm
import time
from requests.exceptions import ChunkedEncodingError

BASE_URL = "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/geuvadis/working/geuvadis_topmed/data/"

def list_subdirs(url):
    """获取指定 URL 下所有一级子目录名（以 / 结尾的链接）"""
    r = requests.get(url, headers={"User-Agent": get_user_agent_of_pc()});
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    subdirs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith("/") and not href.startswith("?"):
            subdirs.append(href.rstrip("/"))
    return subdirs

def download_isoform_results(pop, subdir, output_dir):
    """下载指定子目录下 transcriptome/isoforms.results.tsv 并重命名保存"""
    transcriptome_url = urljoin(BASE_URL, f"{pop}/{subdir}/transcriptome/")
    r = requests.get(transcriptome_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    iso_href = None
    for a in soup.find_all("a", href=True):
        if a["href"].endswith("genes.results.tsv"):
            iso_href = a["href"]
            break
    if not iso_href:
        print(f"Warning: 未找到 isoforms.results.tsv in {transcriptome_url}")
        return
    iso_url = urljoin(transcriptome_url, iso_href)
    local_name = os.path.join(output_dir, f"{subdir}.tsv")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Fetching {iso_url} -> {local_name}")
    for attempt in range(1, 20):
        try:
            resp = requests.get(iso_url, stream=True)
            if resp.status_code == 200:
                total_size = int(resp.headers.get('content-length', 0))
                with open(local_name, "wb") as f, tqdm(
                    desc=f"{subdir}",
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024
                ) as bar:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
                print(f"Downloaded: {local_name}")
                return
            else:
                print(f"HTTP Error: {resp.status_code} on attempt {attempt}")
        except ChunkedEncodingError as e:
            print(f"[{subdir}] Attempt {attempt} failed: {e}")
        except Exception as e:
            print(f"[{subdir}] Other error on attempt {attempt}: {e}")
        time.sleep(2 * attempt)

    print(f"Failed to download {iso_url} after 3 attempts.")

def main(output_dir):
    for pop in ['CEU/', 'FIN/', 'GBR/', 'TSI/', 'YRI/']:
        DES_URL = urljoin(BASE_URL, pop)
        print(f"Fetching {DES_URL}")
        subdirs = list_subdirs(DES_URL)[1:]
        threads = []
        for subdir in subdirs:
            t = threading.Thread(
                target=download_isoform_results,
                args=(pop, subdir, os.path.join(output_dir, pop))
            )
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="1000Genomes CEU isoforms.results.tsv 爬虫")
    parser.add_argument("--output-dir", default=f"./Downloads/Genes", help="本地保存目录")
    args = parser.parse_args()
    main(args.output_dir)
