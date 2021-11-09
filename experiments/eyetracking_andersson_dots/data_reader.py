import numpy as np


class DataReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.__read()

    def __read(self):
        with open(self.file_path, "r") as file_handle:
            file_lines = list(file_handle.readlines())
            file_handle.close()

            # Convert lines to int or float accordingly
            cleaned_data = []
            for index, line in enumerate(file_lines):
                # indexes <= 1 should be convert to int
                cols = line.split(",")
                row = list(map(float, cols[1:5]))
                row.append(int(cols[5]))
                cleaned_data.append(row)

            self.x = []
            self.y = []
            self.distances = []
            self.labels = []
            
            for row in cleaned_data:
                print(row, type(row))
                # Unpack dataset
                (
                    a,
                    b,
                    x,
                    y,
                    label
                ) = row

                # Create distances attr, euclidian distance to (0, 0)
                d = np.sqrt(np.power(x, 2) + np.power(y, 2))

                self.x.append(x)
                self.y.append(y)
                self.distances.append(d)

                # if label == 1, fixation, else saccade
                FIXATION_LABEL = 1
                if label == FIXATION_LABEL:
                    self.labels.append(1)
                else:
                    self.labels.append(0)
