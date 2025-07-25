import os;


def main():
    for pop in ['CEU/', 'FIN/', 'GBR/', 'TSI/', 'YRI/']:
        saveDir = "./Downloads/Genes/" + pop;
        with open(f"{saveDir}/{pop.rstrip('/')}.txt", "w") as f:
            for filename in os.listdir(saveDir):
                f.write(filename.rstrip('.tsv') + "\n") if filename.endswith(".tsv") and not filename.endswith("M.tsv") else None;
            print(f"{pop} done")    


if __name__ == "__main__":
    main();