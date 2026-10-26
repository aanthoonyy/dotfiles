import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#e5e5ea"
    property bool authenticating: false
    property string message: ""
    property date now: new Date()

    function login() {
        if (authenticating || !user.currentText || session.currentIndex < 0)
            return
        message = ""
        authenticating = true
        sddm.login(user.currentText, password.text, session.currentIndex)
    }

    Image {
        anchors.fill: parent
        source: "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: root.now = new Date()
    }

    Column {
        anchors.top: parent.top
        anchors.topMargin: 56
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 5
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDateTime(root.now, "h:mm AP")
            color: "#1d1d1f"
            font.family: "Noto Sans"
            font.pixelSize: 48
            font.weight: Font.Light
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDateTime(root.now, "dddd, MMMM d")
            color: "#636366"
            font.family: "Noto Sans"
            font.pixelSize: 16
        }
    }

    component SoftButton: Button {
        id: button
        font.family: "Noto Sans"
        font.pixelSize: 14
        implicitHeight: 40
        padding: 12
        background: Rectangle {
            radius: 8
            color: button.down ? "#dedee3" : button.hovered ? "#f5f5f7" : "#ffffff"
            border.color: button.activeFocus ? "#0066cc" : "#d1d1d6"
            Behavior on color { ColorAnimation { duration: 100 } }
        }
        contentItem: Text {
            text: button.text
            font: button.font
            color: button.enabled ? "#1d1d1f" : "#8e8e93"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    Rectangle {
        width: 360
        height: form.implicitHeight + 64
        anchors.centerIn: parent
        radius: 16
        color: "#f5f5f7"
        border.color: "#d1d1d6"

        ColumnLayout {
            id: form
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 32
            spacing: 16

            Text {
                text: "Welcome back"
                color: "#1d1d1f"
                font.family: "Noto Sans"
                font.pixelSize: 24
                font.weight: Font.Medium
                Layout.alignment: Qt.AlignHCenter
            }

            ComboBox {
                id: user
                Layout.fillWidth: true
                implicitHeight: 42
                model: userModel
                textRole: "name"
                currentIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
                enabled: !root.authenticating
                font.family: "Noto Sans"
                font.pixelSize: 14
                palette.text: "#1d1d1f"
                background: Rectangle {
                    radius: 8
                    color: "#ffffff"
                    border.color: user.activeFocus ? "#0066cc" : "#d1d1d6"
                }
                onActivated: password.forceActiveFocus()
                KeyNavigation.tab: password
            }

            TextField {
                id: password
                Layout.fillWidth: true
                implicitHeight: 44
                echoMode: TextInput.Password
                placeholderText: "Password"
                color: "#1d1d1f"
                placeholderTextColor: "#8e8e93"
                selectionColor: "#d6e8ff"
                selectedTextColor: "#1d1d1f"
                font.family: "Noto Sans"
                font.pixelSize: 14
                leftPadding: 12
                rightPadding: 12
                enabled: !root.authenticating
                focus: true
                background: Rectangle {
                    radius: 8
                    color: "#ffffff"
                    border.width: password.activeFocus ? 2 : 1
                    border.color: password.activeFocus ? "#0066cc" : "#d1d1d6"
                }
                onAccepted: root.login()
                KeyNavigation.tab: signIn
            }

            Text {
                visible: keyboard.capsLock
                text: "Caps Lock is on"
                color: "#856319"
                font.family: "Noto Sans"
                font.pixelSize: 12
            }

            Text {
                visible: root.message.length > 0
                text: root.message
                color: "#b83b37"
                font.family: "Noto Sans"
                font.pixelSize: 12
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            SoftButton {
                id: signIn
                text: root.authenticating ? "Signing in…" : "Sign in"
                Layout.fillWidth: true
                enabled: !root.authenticating && user.currentText.length > 0 && session.currentIndex >= 0
                onClicked: root.login()
                KeyNavigation.tab: user
                background: Rectangle {
                    radius: 8
                    color: signIn.down ? "#004f9f" : signIn.hovered ? "#1475d4" : "#0066cc"
                    border.color: signIn.activeFocus ? "#1d1d1f" : "transparent"
                    Behavior on color { ColorAnimation { duration: 100 } }
                }
                contentItem: Text {
                    text: signIn.text
                    font: signIn.font
                    color: "#ffffff"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    ComboBox {
        id: session
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 24
        width: 220
        height: 40
        model: sessionModel
        textRole: "name"
        currentIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
        enabled: !root.authenticating
        font.family: "Noto Sans"
        font.pixelSize: 13
        palette.text: "#1d1d1f"
        background: Rectangle {
            radius: 8
            color: "#f5f5f7"
            border.color: session.activeFocus ? "#0066cc" : "#d1d1d6"
        }
    }

    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 8
        SoftButton {
            text: "Sleep"
            visible: sddm.canSuspend
            onClicked: sddm.suspend()
        }
        SoftButton {
            text: "Restart"
            visible: sddm.canReboot
            onClicked: sddm.reboot()
        }
        SoftButton {
            text: "Shut down"
            visible: sddm.canPowerOff
            onClicked: sddm.powerOff()
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.authenticating = false
            root.message = "Couldn't sign in. Check your password and try again."
            password.clear()
            password.forceActiveFocus()
        }
        function onLoginSucceeded() {
            password.clear()
        }
    }

    Component.onCompleted: password.forceActiveFocus()
}
