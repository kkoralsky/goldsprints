
import QtQuick 1.0

Rectangle {
    property variant tabs

    width: tabWidget.width / tabs.length; height: 36

    Rectangle {
        width: parent.width; height: 1
        anchors { bottom: parent.bottom; bottomMargin: 1 }
        color: "#acb2c2"
    }
    BorderImage {
        anchors { fill: parent; leftMargin: 2; topMargin: 5; rightMargin: 1 }
        border { left: 7; right: 7 }
        source: "data/tab.png"
        visible: tabWidget.current == index
    }
    Text {
        horizontalAlignment: Qt.AlignHCenter; verticalAlignment: Qt.AlignVCenter
        anchors.fill: parent
        text: tabs[index]
        elide: Text.ElideRight
        font.bold: tabWidget.current == index
    }
    MouseArea {
        anchors.fill: parent
        onClicked: tabWidget.current = index
    }
}


