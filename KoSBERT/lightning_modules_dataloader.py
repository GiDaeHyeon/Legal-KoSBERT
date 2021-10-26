import torchfrom torch.utils.data import Dataset, DataLoaderfrom transformers import BertTokenizerFastimport pytorch_lightning as plclass KorNLIDataset(Dataset):    def __init__(self,                 phase: str,                 data_dir: str = None,                 tokenizer_weight: str = 'kykim/bert-kor-base',                 max_length: int = None):        super(KorNLIDataset, self).__init__()        if phase == 'train':            data_dir += '/snli_1.0_train.ko.tsv'        elif phase == 'validation':            data_dir += '/xnli.dev.ko.tsv'        elif phase == 'test':            data_dir += '/xnli.test.ko.tsv'        with open(data_dir, 'r') as f:            data = f.readlines()[1:]            self.anchor, self.positive, self.negative = [], [], []            for idx, t in enumerate(data):                tmp = t.split('\t')                if idx % 3 == 0:                    self.anchor.append(tmp[0])                if tmp[2] == 'contradiction\n':                    self.negative.append(tmp[1])                elif tmp[2] == 'entailment\n':                    self.positive.append(tmp[1])                else:                    pass            del data, tmp        assert len(self.anchor) == len(self.positive) and len(self.anchor) == len(self.negative), \            f'Please check the dataset {len(self.anchor)}, {len(self.positive)}, {len(self.negative)}'        self.tokenizer = BertTokenizerFast.from_pretrained(tokenizer_weight)        self.max_length = max_length if max_length is not None else 32    def __len__(self):        return len(self.anchor)    def __getitem__(self, idx):        anchor, positive, negative = self.anchor[idx], self.positive[idx], self.negative[idx]        anchor = self.tokenizer.encode_plus(text=anchor, padding='max_length', max_length=self.max_length)        anchor = {'input_ids': torch.tensor(anchor.get('input_ids')),                  'token_type_ids': torch.tensor(anchor.get('token_type_ids')),                  'attention_mask': torch.tensor(anchor.get('attention_mask'))}        positive = self.tokenizer.encode_plus(text=positive, padding='max_length', max_length=self.max_length)        positive = {'input_ids': torch.tensor(positive.get('input_ids')),                    'token_type_ids': torch.tensor(positive.get('token_type_ids')),                    'attention_mask': torch.tensor(positive.get('attention_mask'))}        negative = self.tokenizer.encode_plus(text=negative, padding='max_length', max_length=self.max_length)        negative = {'input_ids': torch.tensor(negative.get('input_ids')),                    'token_type_ids': torch.tensor(negative.get('token_type_ids')),                    'attention_mask': torch.tensor(negative.get('attention_mask'))}        return anchor, positive, negativeclass KoSBertDataModule(pl.LightningDataModule):    def __init__(self,                 data_dir: str = None,                 tokenizer_weight: str = 'kykim/bert-kor-base',                 max_length: int = None,                 batch_size: int = 64,                 num_workers: int = 4):        super(KoSBertDataModule, self).__init__()        self.train_dataset = KorNLIDataset(phase='train',                                           data_dir=data_dir,                                           tokenizer_weight=tokenizer_weight,                                           max_length=max_length)        self.val_dataset = KorNLIDataset(phase='validation',                                         data_dir=data_dir,                                         tokenizer_weight=tokenizer_weight,                                         max_length=max_length)        self.test_dataset = KorNLIDataset(phase='test',                                          data_dir=data_dir,                                          tokenizer_weight=tokenizer_weight,                                          max_length=max_length)        self.batch_size = batch_size        self.num_workers = num_workers    def train_dataloader(self) -> DataLoader:        return DataLoader(dataset=self.train_dataset,                          batch_size=self.batch_size,                          num_workers=self.num_workers,                          shuffle=True,                          pin_memory=True,                          drop_last=True)    def val_dataloader(self) -> DataLoader:        return DataLoader(dataset=self.val_dataset,                          batch_size=self.batch_size,                          num_workers=self.num_workers,                          shuffle=False,                          pin_memory=False,                          drop_last=False)    def test_dataloader(self) -> DataLoader:        return DataLoader(dataset=self.test_dataset,                          batch_size=self.batch_size,                          num_workers=self.num_workers,                          shuffle=False,                          pin_memory=False,                          drop_last=False)