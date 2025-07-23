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
pop = "CEU"

BASE_URL = f"https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/geuvadis/working/geuvadis_topmed/data/{pop}/"

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

def download_isoform_results(subdir, output_dir):
    """下载指定子目录下 transcriptome/isoforms.results.tsv 并重命名保存"""
    transcriptome_url = urljoin(BASE_URL, f"{subdir}/transcriptome/")
    r = requests.get(transcriptome_url)
    # r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    iso_href = None
    for a in soup.find_all("a", href=True):
        if a["href"].endswith("isoforms.results.tsv"):
            iso_href = a["href"]
            break
    if not iso_href:
        print(f"Warning: 未找到 isoforms.results.tsv in {transcriptome_url}")
        return
    iso_url = urljoin(transcriptome_url, iso_href)
    local_name = os.path.join(output_dir, f"{subdir}.tsv")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Fetching {iso_url} -> {local_name}")
    resp = requests.get(iso_url, stream=True)
    if resp.status_code == 200:
        with open(local_name, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {local_name}")
    else:
        print(f"Warning: 未找到或无法下载 {iso_url} (HTTP {resp.status_code})")

def main(output_dir):
    print(f"Fetching {BASE_URL}");
    subdirs = list_subdirs(BASE_URL)[1:]
    for subdir in subdirs:
        download_isoform_results(subdir, output_dir+"/CEU/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="1000Genomes CEU isoforms.results.tsv 爬虫")
    parser.add_argument("--output-dir", default="./Downloads", help="本地保存目录")
    args = parser.parse_args()
    main(args.output_dir)
