class card:
    """the QR card object.
    """
    qr_path = ''
    public_id = ''


    def __init__(self, qr_path, public_id):
        self.qr_path = qr_path
        self.public_id = public_id
