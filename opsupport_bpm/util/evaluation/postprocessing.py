import os
import sys

def create_global_performance_file(output_dir, file_name):
    fout = open(output_dir + file_name, "w")
    fout.write("HGSIZE \t COL_ANTS \t COLS \t ANTS \t UTI_01 \t TIME \t ACT \t TRANS \t JOINS \t SPLITS\n")
    for file in os.listdir(output_dir):
        sys.stdout.write("Processing file: "+ file + "....")
        if file.startswith("hg_level"):
            file_name_split = str(file).split("_")
            hg_size = file_name_split[2]
            f = open(output_dir + file, "r")
            lines = f.readlines()[1:]
            uti_max = 0
            # get the maximum utility value
            for line in lines:
                split = line.split("\t")
                name, cols, ants, uti, exec_time, act, trans, joins, splits = split
                if float(uti) > uti_max:
                    uti_max = float(uti)
            # rewrite the file contents
            f.close()
            f = open(output_dir + file, "r")
            lines = f.readlines()[1:]
            for line in lines:
                split = line.split("\t")
                name, cols, ants, uti, exec_time, act, trans, joins, splits = split
                fout.write(hg_size + "\t" + str(int(cols)*int(ants)) + "\t" + cols + "\t" + ants + "\t" +
                           str(float(uti)/uti_max) + "\t" + exec_time + "\t" + act + "\t" + trans + "\t" + joins
                           + "\t" + splits)
        else:
            sys.stdout.write("Nothing to process here\n")
        sys.stdout.write("done!\n")
    fout.close()

def create_avg_performance_file():
    output_dir01 = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/run_01/"
    output_dir02 = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/run_02/"
    output_dir03 = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/run_03/"
    file1, file2, file3 = output_dir01 + "total.txt", output_dir02 + "total.txt", output_dir03 + "total.txt"
    out_file = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/average.txt"
    of = open(out_file, "w")
    with open(file1) as f1, open(file2) as f2, open(file3) as f3:
        f1.readline()
        f2.readline()
        f3.readline()
        for line1, line2, line3 in zip(f1, f2, f3):
            hg_size1, cols_ants1, cols1, ants1, uti011, time1, act1, trans1, splits1, joins1 = line1.split("\t")
            hg_size2, cols_ants2, cols2, ants2, uti012, time2, act2, trans2, splits2, joins2 = line2.split("\t")
            hg_size3, cols_ants3, cols3, ants3, uti013, time3, act3, trans3, splits3, joins3 = line3.split("\t")

            of.write(hg_size1 + "\t" + cols_ants1 + "\t" + cols2 + "\t" + ants3 + "\t" +
                     string_avg(uti011, uti012, uti013) + "\t" + string_avg(time1, time2, time3) + "\t" +
                     string_avg(act1, act2, act3) + "\t" + string_avg(trans1, trans2, trans3) + "\t" +
                     string_avg(joins1, joins2, joins3) + "\n")
    of.close()



def string_avg(a, b, c):
    avg = (float(a) + float(b) + float(c))/3
    return str(avg)



if __name__ == "__main__":
    # output_dir01 = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/run_01/"
    # output_dir02 = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/run_02/"
    # output_dir03 = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/run_03/"
    # output_dir04 = "C://opsupport_bpm_files/eval/output_files/results_comint_mag/MMAS_NOLOOPS_BF/run_04/"
    # create_global_performance_file(output_dir01, "total.txt")
    # create_global_performance_file(output_dir02, "total.txt")
    # create_global_performance_file(output_dir03, "total.txt")
    # create_global_performance_file(output_dir04, "total.txt")

    create_avg_performance_file()