import os
import sys
import glob

def create_normalised_uti_files(output_dir):
    """
    Normalises utility by considering the maximum value achieved
    Creates new file with normalised values in /postproc directory
    :param output_dir:
    :return:
    """
    os.makedirs(output_dir + "/postproc")
    for file in os.listdir(output_dir):
        sys.stdout.write("Processing file: "+ file + "....\n")
        for file in glob.glob(output_dir + "/?__hg_level_*"):
        # if file.startswith("?__hg_level"):
            path, file_name = os.path.split(file)
            file_name_split = str(file_name).split("_")
            hg_size = file_name_split[3]
            loop_length = file_name_split[4]
            f = open(file, "r")
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
            f = open(file, "r")
            lines = f.readlines()[1:]
            path, fname = os.path.split(file)
            fname = fname.split(".")[0]
            fname = fname + "_postproc" + ".txt"
            fout = open(path + "/postproc/" + fname, "w")
            fout.write(
                "ROOT \t HGSIZE \t COL_ANTS \t COLS \t ANTS \t UTI_01 \t TIME \t ACT \t TRANS \t JOINS \t SPLITS\n")
            for line in lines:
                split = line.split("\t")
                name, cols, ants, uti, exec_time, act, trans, joins, splits = split
                fout.write(name + "\t" + hg_size + "\t" + loop_length + "\t" + str(int(cols)*int(ants)) + "\t" + cols + "\t" + ants + "\t" +
                           str(float(uti)/uti_max) + "\t" + exec_time + "\t" + act + "\t" + trans + "\t" + joins
                           + "\t" + splits)
            fout.close()
            f.close()
        # else:
        #    sys.stdout.write("Nothing to process here\n")
    sys.stdout.write("done!\n")

def create_global_performance_file(output_dir):
    print("Creating global performance files...")
    if not os.path.exists(output_dir + "/global"):
        print("Creating global directory first...")
        os.makedirs(output_dir + "/global")
    file_global_15 = open(output_dir + "/global/performance_15.txt", "w")
    file_global_25 = open(output_dir + "/global/performance_25.txt", "w")
    print("done.")
    for file_name in os.listdir(output_dir):
        if os.path.isfile(output_dir + "/" + file_name):
            print("\tProcessing file: {0}".format(file_name))
            loop_length = file_name.split("_")[5]
            f = open(output_dir + "/" + file_name, "r")
            for line in f.readlines()[1:]:
                if loop_length == "15":
                    file_global_15.write(line)
                elif loop_length == "25":
                    file_global_25.write(line)
            f.close()
            print("\tdone.")
    file_global_15.close()
    file_global_25.close()
    print("Global files generation completed")

def create_avg_file(output_dir, perf_file, runs_num, loop_size, sizes = []):
    f = open(output_dir + "/" + perf_file, "r")
    d_time = {}
    d_uti = {}
    for line in f.readlines():
        splits = line.split("\t")
        size, colsants, cols, ants, uti, time = int(splits[2]), int(splits[3]), int(splits[4]), int(splits[5]), float(splits[6]), float(splits[7])

        if sizes != []:
            if size in sizes:
                ca_key = (size, cols, ants)
                if ca_key not in d_time:
                    d_time[ca_key] = time
                    d_uti[ca_key] = uti
                else:
                    d_time[ca_key] += time
                    d_uti[ca_key] += uti
        if sizes == []:
            ca_key = (size, cols, ants)
            if ca_key not in d_time:
                d_time[ca_key] = time
                d_uti[ca_key] = uti
            else:
                d_time[ca_key] += time
                d_uti[ca_key] += uti

    for key in d_time:
        d_time[key] = d_time[key] / runs_num
    for key in d_uti:
        d_uti[key] = d_uti[key] / runs_num
    f.close()
    print("Writing avg file...")
    fout = open(output_dir + "/avg" + str(loop_size) +".txt", "w")
    for key in d_time:
        fout.write(str(key[0]) + "\t" + str(key[1]*key[2]) + "\t" + str(key[1]) + "\t" + str(key[2]) + "\t" + str(d_uti[key]) + "\t" + str(d_time[key]) + "\n")
    fout.close()
    print("...done!")






def create_avg_performance_file(postproc_dir, runs_num):
    """
    For each HG_SIZE, creates one new file with averages of utility and execution time
    Finally, it creates a global performance file collating all averages
    TBC
    :param postproc_dir:
    :return:
    """
    for i in range(runs_num):
        print("Processing run: {0}".format(i))
        for file_name in os.listdir(postproc_dir):
            uti_total, time_total = 0, 0
            if file_name.startswith(str(i)):
                print("\tProcess file: {0}".format(file_name))
                f = open(file_name, "r")
                for line in f.readlines:
                    root, size, colsants, cols, ants, uti, time, act, trans, joins, splits = line.split("\t")
                    uti_total += uti
                    time_total += time
                f.close()







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

    # output_dir = "/home/mcomuzzi/IEEE_CIMAG_results/mmas_noloops_bf"
    output_dir = "/home/mcomuzzi/IEEE_CIMAG_results/acs_noloops_bf"
    output_dir = "/home/mcomuzzi/opsupport_bpm_files/postprocessing/loops/bf"


    # file = output_dir + "/file.txt"
    # head, tail = os.path.split(file)
    # print(head)
    # print(tail)
    # path, fname = os.path.split(file)
    # fname = fname.split(".")[0]
    # fname = fname + "_postproc" + ".txt"
    # print(path + "/" + fname)


    # create_normalised_uti_files(output_dir)


    # create_global_performance_file(output_dir + "/postproc")

    create_avg_file(output_dir + "/postproc/global", "performance_15.txt", 4.0, 15)
    create_avg_file(output_dir + "/postproc/global", "performance_25.txt", 4.0, 25)
