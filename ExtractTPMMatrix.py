import pandas;
import os;


def main():
    for pop in ['CEU/', 'FIN/', 'GBR/', 'TSI/', 'YRI/']:
        tpmDF = pandas.DataFrame();
        fpkmDF = pandas.DataFrame();
        saveDir = "./Downloads/" + pop;
        for filename in os.listdir(saveDir):
            if filename.endswith(".tsv"):
                filePath = os.path.join(saveDir, filename);
                df = pandas.read_csv(filePath, sep="\t");
                tpmDF[filename[:-4]] = df["TPM"];
                fpkmDF[filename[:-4]] = df["FPKM"];
        fpkmDF.index = df["gene_id"];
        tpmDF.index = df["gene_id"];
        tpmDF.to_csv("./Downloads/" + pop + f"{pop.rstrip('/')}_TPM.tsv", sep="\t", index=True);
        print(f"{pop} done on TPM");
        fpkmDF.to_csv("./Downloads/" + pop + f"{pop.rstrip('/')}_FPKM.tsv", sep="\t", index=True);
        print(f"{pop} done on FPKM");


if __name__ == "__main__":
    main();