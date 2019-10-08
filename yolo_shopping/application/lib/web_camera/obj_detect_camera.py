from time import sleep
from PIL import Image
import numpy as np
import io
import cv2
from application.lib.yolo import YOLO


class ObjDetectCamera:
    def __init__(self, fps=30.0, device_num=0, cam_scale=1.0):
        self.fps = fps                                     # 秒間フレーム数
        self.camera = cv2.VideoCapture(device_num)         # カメラデバイスを取得
        self.yolo = YOLO()                                 # YOLOモデルのオブジェクト化
        self.cam_scale = cam_scale                         # フレームサイズを変換するときの倍率
        self.frame_bin = None                              # フレームのバイナリをストアする場所

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

            # フレームサイズの変換 ===================
            h, w = frame.shape[:2]
            rh = int(h * self.cam_scale)
            rw = int(w * self.cam_scale)
            frame = cv2.resize(frame, (rw, rh))
            # frame = frame[:, :, (2, 1, 0)]

            # ndarrayをバイナリデータに変換(さらに物体検出の実行) ==========
            # - バイナリを格納するバッファを作る
            img_buf = io.BytesIO()
            # - ndarrayをPILのImageに変換
            p_img = Image.fromarray(np.uint8(frame))
            # - 物体検出後の画像を取得
            p_img = self.yolo.detect_image(p_img)
            # - Imageをバッファに保存
            p_img.save(img_buf, format='JPEG')
            # - バイナリを取得
            img_bin = img_buf.getvalue()
            # - インスタンス変数に格納
            self.frame_bin = (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + img_bin + b'\r\n')

            # UIに渡すデータを生成
            yield {
                "frame_data": (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + img_bin + b'\r\n'),
                "objects": self.yolo.fetch_objects()
            }
            # フレーム撮影のインターバルを取る
            sleep(1 / self.fps)
        self.yolo.close_session()

    def __del__(self):
        if self.camera:
            self.camera.release()
            cv2.destroyAllWindows()

    def frame_generator(self):
        while True:
            if not self.frame_bin:
                # 取り急ぎダミー画像を入れる
                yield "https://imgur.com/H3cLmFY"
            else:
                yield self.frame_bin
            sleep(1 / self.fps)
