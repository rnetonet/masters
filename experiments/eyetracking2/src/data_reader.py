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
                cleaned_data.append(list(map(float, line.split())))

            # Unpack dataset
            (
                self.x,
                self.y,
                self.x_filt,
                self.y_filt,
                self.vel_x,
                self.vel_y,
                self.vel,
                self.acc,
                self.velx_filt,
                self.vely_filt,
                self.vel_filt,
                self.acc_filt,
            ) = cleaned_data


            # Create distances attr, euclidian distance to (0, 0)
            self.distances = []
            for _x, _y in zip(self.x, self.y):
                d = np.sqrt(np.power(_x, 2) + np.power(_y, 2))
                self.distances.append(d)