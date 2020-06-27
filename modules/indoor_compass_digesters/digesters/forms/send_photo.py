import logging, datetime
from modules.pytg.ModulesLoader import ModulesLoader
import torch
from torchvision import transforms
from torch import nn
from PIL import Image
import pandas as pd

def send_photo_digester(bot, chat_id, form_entries, form_meta):
    logging.info("Send_photo digesting ({}, {}, form_meta)".format(chat_id, form_entries, form_meta))
    model = torch.load(ModulesLoader.get_module_content_folder("indoor_compass") + "/indoor_compass_model/resnet18_400.pt")
    model.eval()
    newFile = bot.get_file(form_entries['media_id'])
    photo_path = ModulesLoader.get_module_content_folder("indoor_compass")+ "/indoor_compass_tmp_photo/photo.jpeg"
    newFile.download(photo_path)

    ### OPEN IMAGE ###
    photo = Image.open(photo_path)
    mean_list = [0.33210807, 0.29329791, 0.26337797]
    std_list = [0.24047631, 0.23936823, 0.24046722]
    mean = torch.FloatTensor(mean_list)
    print(mean)
    std = torch.FloatTensor(std_list)
    print(std)
    photo_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean,std)])

    ### MODEL'S PREDICTION ###
    photo = photo_transform(photo)
    output = model(photo.view(-1, 3, 224, 224))

    ### OUTPUT IN RANGE [0,1] ###
    softmax = nn.Softmax()
    preds_softmax = softmax(output.detach().to('cpu'))
    preds_softmax = preds_softmax.numpy().tolist()
    preds_softmax = [val for sublist in preds_softmax for val in sublist]

    ### CREATE OUTPUT TEXT SORTED FOR PROBABILITY ###
    labels = ["Forward","Right","Left"]
    preds = pd.DataFrame(
        {'Direction': labels,
         'Probability': preds_softmax,
         })
    preds.Probability = preds.Probability.astype(float)
    preds = preds.sort_values('Probability', ascending=False)

    ### SEND REPLY ###
    bot.send_message(chat_id=chat_id, text=preds.to_string())

    ### SEND ONLY THE MAX VALUE ###
    # prediction = preds_softmax.to('cpu').max(1)[1]
    # if(prediction==0):
    #     bot.send_message(chat_id=chat_id, text="Forward!")
    # elif(prediction==1):
    #     bot.send_message(chat_id=chat_id, text="Right!")
    # else:
    #     bot.send_message(chat_id=chat_id, text="Left!")
