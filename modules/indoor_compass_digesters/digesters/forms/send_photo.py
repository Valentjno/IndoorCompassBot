import logging, datetime
from modules.pytg.ModulesLoader import ModulesLoader
import torch
from torchvision import transforms
import cv2
from PIL import Image
def send_photo_digester(bot, chat_id, form_entries, form_meta):
    logging.info("Send_photo digesting ({}, {}, form_meta)".format(chat_id, form_entries, form_meta))
    model = torch.load(ModulesLoader.get_module_content_folder("indoor_compass") + "/indoor_compass_model/model.pt")
    model.eval()
    newFile = bot.get_file(form_entries['media_id'])
    photo_path = ModulesLoader.get_module_content_folder("indoor_compass")+ "/indoor_compass_tmp_photo/photo.jpeg"
    newFile.download(photo_path)

    photo = Image.open(photo_path)
    #photo = cv2.imread(photo_path)
    photo_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor()])
    photo = photo_transform(photo)
    #out = nnf.interpolate(photo, size=(1,3,244,244), mode='bicubic', align_corners=False)
    output = model(photo.view(-1, 3, 224, 224))
    prediction = output.to('cpu').max(1)[1]
    if(prediction==0):
        bot.send_message(chat_id=chat_id, text="Forward!")
    elif(prediction==1):
        bot.send_message(chat_id=chat_id, text="Right!")
    else:
        bot.send_message(chat_id=chat_id, text="Left!")
