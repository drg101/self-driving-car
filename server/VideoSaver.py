from csv import writer
import threading

class VideoSaver:
    MAX_BUFFER_SIZE = 20
    def __init__(labels_path, images_folder):
        self.img_buffer = []
        self.img_timestamps = []
        self.size = 0
        self.labels_path = labels_path
        self.images_folder = images_folder

        self.init_csv()
    def init_csv():
        # write header first
        with open(self.labels_path, 'w') as f:
            labels_file = writer(f)
            labels_file.writerow(["timestamp", "forward/backward", "left/right"])
    
    def save(self, img, timestamp, controlDict):
        '''
            img - cv2 image
        '''
        self.size += 1

        fw = controlDict['fw']
        lr = controlDict['lr']
        self.img_buffer.append(img_buffer)
        self.img_timestamps.append(timestamp)
        with open(self.labels_path, 'a') as f:
            labels_file = writer(f)
            labels_file.writerow([timestamp, fw, lr])
        if self.size > MAX_BUFFER_SIZE:
            self.clear_img_buffer()
            self.img_buffer.clear()
            self.img_timestamps.clear()


    def clear_img_buffer(self):
        for i, img in enumerate(self.img_buffer):
            file_name = 'img_' + self.img_timestamps[i] + '.jpeg'
            file_path = self.images_folder / file_name
            cv2.imwrite(file_path, img)


        