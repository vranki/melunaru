import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

ApplicationWindow {
    width: 640
    height: 480
    visible: true
    title: qsTr("Melunaru Mixer")

    Component.onCompleted: melunaru.start()

    header: Label {
        text: "Melunaru"
    }
    RowLayout {
        Layout.fillHeight: true
        Repeater {
            model: melunaru ? melunaru.sourceCount() : 0
            GroupBox {
                width: 100
                Layout.fillWidth: true
                title: "Source " + index

                ColumnLayout {
                    anchors.fill: parent
                    Label {
                        color: melunaru.sourceStatus(index) ? "green" : "red"
                        text: melunaru.sourceStatus(index) ? "OK" : "FAIL"
                    }

                    Slider {
                        id: volumeSlider
                        orientation: Qt.Vertical
                        Layout.fillHeight: true
                        value: 1
                        wheelEnabled: true
                        onValueChanged: melunaru.setVolume(index, value)
                    }
                    Label {
                        text: Math.round(volumeSlider.value * 100) + " %"
                    }
                }
            }
        }
    }
}
