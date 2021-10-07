from torch.nn import Conv2d, ReLU, MaxPool2d, Linear, Module
from torch import flatten

class ChessConvNet(Module):
    def __init__(self, square_size=80, out_channels=10):
        super(ChessConvNet, self).__init__()
        self.in_channels = 3
        self.out_channels = out_channels
        self.out_vector_length = 13

        self.relu = ReLU(inplace=True)
        self.maxpool1 = MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
        self.maxpool2 = MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)

        self.conv1 = Conv2d(self.in_channels, 10, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv2 = Conv2d(10, 20, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv3 = Conv2d(20, 20, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv4 = Conv2d(20, 10, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv5 = Conv2d(10, self.out_channels, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))

        infeatures = int(self.out_channels * (square_size / 4) ** 2)
        self.linear1 = Linear(in_features=infeatures, out_features=500, bias=True)
        self.linear2 = Linear(in_features=500, out_features=500, bias=True)
        self.linear3 = Linear(in_features=500, out_features=13, bias=True)


    def forward(self, x):
        out = self.conv1(x)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.relu(out)
        out = self.conv3(out)
        out = self.relu(out)
        out = self.conv4(out)
        out = self.relu(out)
        out = self.maxpool1(out)
        out = self.conv5(out)
        out = self.relu(out)
        out = self.maxpool2(out)

        out = flatten(out, 1)

        out = self.linear1(out)
        out = self.linear2(out)
        out = self.linear3(out)

        return out
