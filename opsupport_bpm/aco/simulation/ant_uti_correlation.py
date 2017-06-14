import logging
from os import listdir


class AntUtilityCorrelator:
    """
    This class creates (number of ants)-(utility) correlation data using the simulation data
    created by a GUI simulation
    """



    def __init__(self):
        self.logger = logging.getLogger()



    def __init__(self, input_path, output_path):
        self.logger = logging.getLogger()
        self.input_path = input_path
        self.output_path = output_path

    def process_simulation_files(self):
        self.logger.info("Processing output file for scatter plot...")
        out_file = open(self.output_path + "scatter.txt", 'w')
        firstline = "NODES \t COL \t ANT \t ANTS \t EXPLORE \t UTILITY" + '\n'
        out_file.write(firstline)
        for file in listdir(self.input_path + "\performance"):
            file_name = self.input_path + "\performance\\" + file
            self.logger.info("Processing file: {0}".format(file))
            f = open(file_name, 'r')
            lines = f.readlines()[1:]
            # check max utility
            last_line = lines[len(lines)-1]
            last_line_split = last_line.split('\t')
            max_utility = float(last_line_split[3])
            for line in lines:
                line_split = line.split('\t')
                nodes = line_split[6]
                col_num, ant_num, utility = int(line_split[1]), int(line_split[2]),  float(line_split[3]) / max_utility
                total_ants = col_num * ant_num
                out_file.write(str(nodes) + "\t" + str(col_num) + '\t' + str(ant_num) + '\t' + str(total_ants) + '\t' + str(utility) + '\n')
            f.close()
        out_file.close()
        self.logger.info("...done")

    def postprocessing_simulation_ONE(self):
        self.logger.info("Processing output file for scatter plot...")
        out_file = open(self.output_path + "one_scatter.txt", 'w')
        out_file.write('ROOT \t COL \t ANT \t ANTS \t EXPLORE \t UTILITY' + '\n')
        file_name = self.input_path + '\performance\sim_results_ONE.txt'
        #self.logger.info("Processing file: {0}".format(file))
        f = open(file_name, 'r')
        lines = f.readlines()[1:]
        # check max utility
        last_line = lines[len(lines) - 1]
        last_line_split = last_line.split('\t')
        # max_utility = float(last_line_split[3])
        for line in lines:
            line_split = line.split('\t')
            max_utility = self.max_utility(line_split[0], self.output_path + '\performance\sim_results_ONE.txt')
            root, col_num, ant_num, explore, utility = line_split[0], int(line_split[1]), int(line_split[2]), int(line_split[3]), float(
                line_split[4]) / max_utility
            out_file.write(
                root + '\t' + str(col_num) + '\t' + str(ant_num) + '\t' + str(explore) + '\t' + str(utility) + '\n')
        f.close()

        out_file.close()
        self.logger.info("...done")


    def max_utility(self,root, input_file_name):
        f = open(input_file_name, "r")
        opt = 0
        for line in f.readlines():
            values = line.split('\t')
            uti, curr_root = values[4], values[0]
            if root == curr_root:
                if float(uti) > opt:
                    opt = float(uti)
        f.close()
        return opt


    def extract_opt_ants_uti(self, out_file):
        with open(out_file) as f:
            lines = f.readlines()

        curr_col_num, curr_col_ant, curr_utility = 0, 0 ,0
        for line in lines:
            line_split = line.split('\t')
            col_num, ant_num, utility = line_split[1], line_split[2], line_split[4]
            if utility == curr_utility:
                self.logger.debug("Found optimal colony and ant_number: {0}, {1}, {2}".format(col_num, ant_num, utility))
                total_ants = col_num * ant_num
        return ant_num, col_num, total_ants, utility







if __name__ == '__main__':

    input_path = "C://opsupport_bpm_files/eval/output_files/"
    output_path = "C://opsupport_bpm_files/eval/output_files/"

    AUC = AntUtilityCorrelator(input_path, output_path)

    AUC.process_simulation_files()
    #AUC.postprocessing_simulation_ONE()

