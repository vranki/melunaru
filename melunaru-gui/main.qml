import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

ApplicationWindow {
    id: mainWindow
    width: 640
    height: 480
    visible: true
    title: qsTr("Melunaru Mixer")

    property int sourceCount: 0
    property var sourceStatuses: []
    property var sourceNames: []
    property bool connected: false

    onSourceCountChanged: {
        while(sourceStatuses.length > sourceCount) {
            sourceStatuses.pop()
        }
        while(sourceStatuses.length < sourceCount) {
            sourceStatuses.push(false)
        }
        while(sourceNames.length > sourceCount) {
            sourceNames.pop()
        }
        while(sourceNames.length < sourceCount) {
            sourceNames.push('')
        }
    }

    Component.onCompleted: melunaru.start()

    Connections {
        target: melunaru
        function onUpdated() {
            connected = true
            connectedTimer.restart()
            sourceCount = melunaru.sourceCount()
            var newStatuses = []
            for(var i=0;i < sourceCount; i++) {
                newStatuses.push(melunaru.sourceStatus(i) > 0)
            }
            sourceStatuses = newStatuses
            var newNames = []
            for(i=0;i < sourceCount; i++) {
                newNames.push(melunaru.sourceName(i))
            }
            sourceNames = newNames
        }
    }

    Timer {
        id: connectedTimer
        interval: 5000
        repeat: true
        onTriggered: {
            connected = false
            melunaru.update()
        }
    }

    header: ToolBar {
        Label {
            text: connected ? "Connected" : "Disconnected"
        }
    }

    RowLayout {
        Layout.fillHeight: true
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        Repeater {
            model: sourceCount
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.maximumWidth: 150
                Layout.preferredWidth: 150

                title: sourceNames[index].length ? sourceNames[index] : "Source " + index
                ColumnLayout {
                    anchors.fill: parent
                    Label {
                        color: sourceStatuses[index] ? "green" : "red"
                        text: sourceStatuses[index] ? "OK" : "FAIL"
                    }
                    CheckBox {
                        text: "CUE"
                        onCheckedChanged: melunaru.setCue(index, checked ? 1 : 0)
                    }
                    Slider {
                        id: volumeSlider
                        orientation: Qt.Vertical
                        Layout.fillHeight: true
                        value: 0
                        from: 0
                        to: 2
                        wheelEnabled: true
                        onValueChanged: melunaru.setVolume(index, value)
                        Timer {
                            interval: 1000
                            onTriggered: melunaru.setVolume(index, parent.value)
                            repeat: true
                            running: connected
                        }
                    }
                    Label {
                        text: Math.round(volumeSlider.value * 100) + " %"
                    }
                }
            }
        }
    }
}
