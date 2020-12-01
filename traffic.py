import requests
import os

# URLs
traffic_cam_num = 52
url = 'https://5723acd20ffa9.streamlock.net:1935/lexington-live/lex-cam-0'+ str(traffic_cam_num) + '.stream/'
playlist_url = 'playlist.m3u8'

file_path = 'C:\\Users\\chaud\\Desktop\\!Back_this_folder!\\!Back_this_folder_up_old!\\Coding and AI\\python\\Lexington Traffic Project\\'
name_of_playlist ='playlist.txt'

#Makes folder
media_folder_path = file_path + 'media_' + str(traffic_cam_num) + '\\'
if not os.path.exists(media_folder_path):
    os.makedirs(media_folder_path)

video_record = []

while True:
    #Gets First Part of number
    playlist = requests.get(url = url + playlist_url)
    playlist_txt = open( file_path + name_of_playlist, 'wb')
    playlist_txt.write(playlist.content)
    playlist_txt = open( file_path + name_of_playlist, 'r')
    first_numbers = playlist_txt.readlines()[3] 
    playlist_txt.close()

    under_score_index = first_numbers.find('_')
    dot_index = first_numbers.find('.')

    first_numbers = first_numbers[int(under_score_index) +1 : int(dot_index)]
    # print(first_numbers)
    playlist_txt.close()

    #Gets Chunklist
    chunklist_url = 'chunklist_' + first_numbers 

    chunklist = requests.get(url = url + chunklist_url + '.m3u8')
    chunklist_txt = open(file_path + chunklist_url + '.txt', 'wb')
    chunklist_txt.write(chunklist.content)
    chunklist_txt = open(file_path + chunklist_url + '.txt', 'r')
    chunklist_lines = chunklist_txt.readlines()[5:]
    chunklist_txt.close()
    os.remove(file_path + chunklist_url + '.txt')

    for lines in chunklist_lines:
        if lines[0] !='#':
            lines = lines[:-1]

            
            if len(video_record) >=3:
                if lines[-8:-3] == video_record[-1] or lines[-8:-3] == video_record[-2] or lines[-8:-3] == video_record[-3]:
                    print('Line: ' + str(lines[-8:-3] + ' | video_record: ' + str(video_record[-3]) + ' '+ str(video_record[-2]) + ' '+ str(video_record[-1]) + ' '))
                    print('Broke')
                    break
            
            if not os.path.isfile(media_folder_path + str(lines)):
                
                video = requests.get(url = url + lines)
                video_path = open(media_folder_path + str(lines), 'xb')

                video_path.write(video.content)
                video_path.close()
                video_record.append(lines[-8:-3])
                video_record.pop(0)
                print(lines)
                print(video_record)

                    

   



