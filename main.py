from qrcode import QRCodeGenerator # type: ignore
QR = QRCodeGenerator()
QR.generate(input(), 'cc.png')