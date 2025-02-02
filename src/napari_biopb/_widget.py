from typing import TYPE_CHECKING

from grpc import RpcError
from magicgui.widgets import ComboBox, Container, ProgressBar, create_widget

if TYPE_CHECKING:
    import napari


# if we want even more control over our widget, we can use
# magicgui `Container`
class BiopbImageWidget(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer

        self._image_layer_combo = create_widget(
            label="Image", annotation="napari.layers.Image"
        )

        # self._roi = create_widget(
        #     label="ROI",
        #     annotation="napari.layers.Shapes",
        #     options={"nullable":True},
        # )

        self._is3d = create_widget(label="3D", annotation=bool)

        self._server = create_widget(
            value="lacss.biopb.org",
            label="Server",
            annotation=str,
        )

        self._threshold = create_widget(
            value=0.4,
            label="Min Score",
            annotation=float,
            widget_type="FloatSlider",
            options={"min": 0, "max": 1},
        )

        self._use_advanced = create_widget(
            value=False,
            label="Advanced",
            annotation=bool,
        )
        self._use_advanced.changed.connect(self._activte_advanced_inputs)

        self._size_hint = create_widget(
            value=35.0,
            label="Size Hint",
            annotation=float,
            widget_type="FloatSlider",
            options={"min": 10, "max": 200, "visible": False},
        )

        self._nms = ComboBox(
            value="Off",
            choices=["Off", "Iou-0.2", "Iou-0.4", "Iou-0.6", "Iou-0.8"],
            label="NMS",
            visible=False,
        )

        self._pixel_size_x = create_widget(
            value=1.0,
            label="Pixel Size X",
            options={"visible": False},
        )

        self._pixel_size_y = create_widget(
            value=1.0,
            label="Pixel Size Y",
            options={"visible": False},
        )

        self._pixel_size_z = create_widget(
            value=1.0,
            label="Pixel Size Z",
            options={"visible": False},
        )

        self._scheme = ComboBox(
            value="Auto",
            choices=["Auto", "HTTP", "HTTPS"],
            label="Scheme",
            visible=False,
        )

        self._run_button = create_widget(label="Run", widget_type="Button")
        self._run_button.changed.connect(self.run)

        self._progress_bar = ProgressBar(
            label="Running", value=0, step=1, visible=False
        )

        self._elements = [
            self._image_layer_combo,
            # self._roi,
            self._is3d,
            self._server,
            self._threshold,
            self._use_advanced,
            self._size_hint,
            self._nms,
            self._pixel_size_x,
            self._pixel_size_y,
            self._pixel_size_z,
            self._scheme,
            self._run_button,
            self._progress_bar,
        ]

        # append into/extend the container with your widgets
        self.extend(self._elements)

    def _activte_advanced_inputs(self):
        for ctl in [
            self._size_hint,
            self._nms,
            self._pixel_size_x,
            self._pixel_size_y,
            self._pixel_size_z,
            self._scheme,
        ]:
            ctl.visible = self._use_advanced.value

    def snapshot(self):
        return {w.label: w.value for w in self._elements}

    def run(self):
        from ._grpc import grpc_call

        name = self._image_layer_combo.value.name + "_label"

        self._run_button.enabled = False
        self._run_button.visible = False

        self._progress_bar.visible = True
        self._progress_bar.value = 0

        try:
            labels = grpc_call(self)

            if name in self._viewer.layers:
                self._viewer.layers[name].data = labels
            else:
                self._viewer.add_labels(labels, name=name)

        except RpcError as err:
            print(err)
            # print(err.details())
        # except Exception as all_err:
        #     print(all_err)

        self._progress_bar.visible = False
        self._run_button.enabled = True
        self._run_button.visible = True
