from time import sleep
from PIL import Image
import numpy as np
import io
import cv2


class WebCamera:
    def __init__(self, fps=30.0, device_num=0):
        self.fps = fps                                     # 秒間フレーム数
        self.camera = cv2.VideoCapture(device_num)         # カメラデバイスを取得

    def __call__(self, *args, **kwargs):
        if not self.camera:
            self.camera = cv2.VideoCapture(0)
        while True:
            # Webカメラからキャプチャ情報を取得
            # frameはndarrayのインスタンスになる
            ret, frame = self.camera.read()
            # OpenCVはデフォルトでBGRという色設定なので、RGBに変換する
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # breakパターン ========================
            # - なんかキャプチャ失敗したとき
            if not ret:
                break
            # - ESCキー押されたとき
            k = cv2.waitKey(1)
            if k == 27:
                break

            # ndarrayをバイナリデータに変換 ==========
            # - バイナリを格納するバッファを作る
            img_buf = io.BytesIO()
            # - ndarrayをPILのImageに変換
            p_img = Image.fromarray(np.uint8(frame))
            # - Imageをバッファに保存
            p_img.save(img_buf, format='JPEG')
            # - バイナリを取得
            img_bin = img_buf.getvalue()

            # フレームをバイナリデータで出力
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_bin + b'\r\n')
            # フレーム撮影のインターバルを取る
            sleep(1 / self.fps)

    def __del__(self):
        if self.camera:
            self.camera.release()
            cv2.destroyAllWindows()

