import sys, pdb
sys.path.extend(['/Users/zeerakw/Documents/PhD/projects/Generalisable_abuse'])

from tqdm import tqdm
import torch.nn as nn
import torch.optim as optim
import gen.shared.types as t
from gen.shared.clean import Cleaner
from gen.shared.train import create_batches, compute_unigram_liwc
from gen.neural import LSTMClassifier


def setup_data():
    device = 'cpu'
    data_dir = '/Users/zeerakw/Documents/PhD/projects/Generalisable_abuse/data/'
    cleaning = ['lower', 'url', 'hashtag', 'username']
    clean = Cleaner(cleaning)

    # Davidson
    text = (t.text_data, {'attribute': ['tokenize', 'preprocessing'],
                          'value': [clean.tokenize, compute_unigram_liwc]})
    # text = (t.text_data, {'attribute': ['tokenize'],
    #                       'value': [clean.tokenize]})
    label = (t.int_label, None)

    # dict_fields = {'': None, kk}

    fields = [('empty', None), ('CF_count', None), ('hate_speech', None), ('offensive', None), ('neither', None),
              ('label', label[0]), ('text', text[0])]

    data_opts = {'splits': {'train': 'davidson_test.csv'}, 'ftype': 'csv', 'data_field': text, 'fields': fields,
                 'label_field': label, 'batch_sizes': (64,), 'shuffle': True, 'skip_header': True,
                 'repeat_in_batches': False, 'split_ratio': 0.8}

    ds = create_batches(data_dir = data_dir, device = device, **data_opts)

    return ds


def train(epochs, data, model, loss_func, optimizer):

    for epoch in tqdm(range(epochs)):
        model.zero_grad()
        batch = next(iter(train))

        scores = model(batch)
        loss = loss_func(scores, batch.labels)
        loss.backward()
        optimizer.step()


# TODO Implement metrics
# TODO Get class of the predicted label
ds, train_batch, dev_batch, test_batch, vocab = setup_data()

HIDDEN_DIM = 300
NO_CLASSES = 3
NO_LAYERS = 2
VOCAB_SIZE = len(vocab)

model = LSTMClassifier(hidden_dim = HIDDEN_DIM, input_dim = VOCAB_SIZE, no_classes = NO_CLASSES, no_layers = NO_LAYERS)
optimizer = optim.Adam(model.parameters(), lr = 0.01)
loss = nn.NLLLoss()

train(300, train_batch, model, loss, optimizer)
