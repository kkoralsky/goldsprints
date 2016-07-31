import Qt 4.7

Item {
    id: tabWidget
    property int current: 0
    //property int dist: 0

    property bool yes_youre_racing: false
    property bool race_prepared: false
    //property variant round
    property list<Item> finals

    onCurrentChanged: setOpacities()
    Component.onCompleted: {
        setOpacities();
    }

    function start() {
        console.log('starrt')
    }

    function abort() {
        red_bar.width=0
        blue_bar.width=0
        yes_youre_racing=false

        race_prepared=false
    }

    function finish(blue_res, red_res) {
        abort()

        console.log(blue_res,red_res)

        var winner = blue_res<red_res ? blue_input.text : red_input.text
        for(var i=finals.children.length-1; i>=0; i--) {

            if(finals.children[i].id=="finals_"+current) {
                var races=finals.children[i].children[0]

                for(var j=0; j<races.children.length-1; j++) {

                    races.children[j].children[0].children[0].children[0].font.bold=false
                    races.children[j].children[1].children[0].children[0].font.bold=false
                    if(races.children[j].blue_player.toUpperCase()==winner)
                        races.children[j].children[0].children[0].children[0].font.bold=true
                    else if(races.children[j].red_player.toUpperCase()==winner)
                        races.children[j].children[1].children[0].children[0].font.bold=true
                }

            }

        }

        red_input.text=""
        blue_input.text=""
        sets_red.chosen=0
        sets_blue.chosen=0

    }
    function new_race(blue, red) {
        blue_input.text=blue
        red_input.text=red

        race_prepared=true
    }

    function update_race(player,pos,time,speed) {
        if(player===0) {
            blue_bar.width=blue_bar.parent.width*pos/dist

           }
        else if(player===1) {
            red_bar.width=red_bar.parent.width*pos/dist

        }
    }

    function setOpacities() {
        //console.log(finals.children[0].opacity)
        for (var i = 0; i < finals.children.length; ++i) {
            finals.children[i].opacity=finals.children[i].id=='finals_'+current
        }
    }

    width: 640; height: 480;

    Column {
        y: 10
            Column {
                spacing: 10
                anchors.horizontalCenter: parent.horizontalCenter



                Column {
                Rectangle { border.color: "blue"; border.width: 4;
                    anchors.topMargin: 10
                    height: 30; width: 500
                    Rectangle {
                        id: blue_bar
                        x:0;y:0
                        height:parent.height
                        color: parent.border.color
                    }
                    TextInput {
                        anchors.verticalCenter: parent.verticalCenter;
                        anchors.margins: 4
                        anchors.fill: parent
                        validator:  RegExpValidator { regExp: /.{,15}/}
                        font.pixelSize: 17
                        font.bold: yes_youre_racing
                        enabled: ! yes_youre_racing
                        focus: true
                        id: blue_input
                        KeyNavigation.tab: red_input
                        Keys.onReturnPressed: {
                            if(race_prepared)
                                btn_start.clicked();
                            else
                                btn_new_race.clicked();
                        }

                    }
                }
                Row {
                Repeater {
                    model: sets;
                    id: sets_blue
                    property int chosen: 0
                    height: 15; width: parent.children[0].width
                    delegate:
                        Rectangle {
                            width: 20*modelData.length
                            id: blue_rect_set
                            height: 20
                            border { color: "blue"; width: 4 }
                            Text { anchors.centerIn: parent;
                                text: modelData; font.bold: yes_youre_racing }
                            MouseArea { anchors.fill: parent;
                                enabled: ! yes_youre_racing
                                onClicked: sets_blue.chosen=index
                            }
                            states: [ State { name: "clicked";
                                              when: sets_blue.chosen==index
                                    PropertyChanges { target: blue_rect_set; color: "blue" }

                                } ]
                    }

                }
                }
                }

                Column {
            Rectangle {
                border.color: "red"; border.width: 4; height: 30; width: 500
                Rectangle {
                    id: red_bar
                    x:0;y:0
                    height:parent.height

                    color: parent.border.color
                }
                TextInput { font.pixelSize: 17;
                    //font.bold: yes_youre_racing
                    anchors { margins:4; verticalCenter: parent.verticalCenter; fill: parent }
                    id: red_input
                    font.bold: yes_youre_racing
                    enabled: ! yes_youre_racing
                    validator: RegExpValidator { regExp: /.{,15}/ }
                    KeyNavigation.tab: blue_input
                    Keys.onReturnPressed: {
                        if(race_prepared)
                            btn_start.clicked();
                        else
                            btn_new_race.clicked();
                    }
                }

            }
            Row {
            Repeater {
                model: sets
                id: sets_red
                property int chosen: 0

                height: 15; width: parent.children[0].width
                delegate:
                    Rectangle {
                        id: red_rect_set
                        width: 20*modelData.length

                        height: 20
                        border { color: "red"; width: 4 }
                        Text { anchors.centerIn: parent;
                            text: modelData; font.bold: yes_youre_racing

                        }
                        MouseArea { anchors.fill: parent;
                            enabled: ! yes_youre_racing
                            onClicked: sets_red.chosen=index
                        }
                        states: [
                            State { name: "clicked"; when: sets_red.chosen==index
                                PropertyChanges { target: red_rect_set; color: "red" }
                            }
                        ]
                }
            }
            }



            }
                Row { spacing:  10
                    anchors.horizontalCenter: parent.horizontalCenter
                    Btn { text: "New race";
                        enabled: ! yes_youre_racing
                        id: btn_new_race;
                        onClicked: {
                        if(race_prepared) {
                            red_input.text=""
                            blue_input.text=""
                            race_prepared=false
                        } else if (red_input.text.length+blue_input.text.length>0) {
                           var res=cmd.new_race(blue_input.text, red_input.text,
                                                     sets[sets_blue.chosen], sets[sets_red.chosen])

                           if(res.search(/.+(blue) and.+(red)/))
                               race_prepared=true
                            else
                               console.log(res)
                        }

                        }
                    }

                    Btn { text: "Swap";
                          enabled: (! yes_youre_racing) && race_prepared;
                          id: btn_swap;
                    onClicked: {
                        var tmp_n=red_input.text
                        var tmp_s=sets_red.chosen

                        red_input.text=blue_input.text
                        sets_red.chosen=sets_blue.chosen
                        blue_input.text=tmp_n
                        sets_blue.chosen=tmp_s
                        cmd.swap()
                    }
                    }
                    Btn { text: yes_youre_racing ? "Abort" : "Start"
                        id: btn_start;
                        enabled: race_prepared
                        onClicked: {
                      if(yes_youre_racing) {
                          abort()
                          cmd.abort()
                      } else
                          cmd.start()

                      yes_youre_racing = !yes_youre_racing

                  }
            }


            }

            Btn { size: 15; text: "show sponsors"; onClicked: cmd.sponsors() }

            Btn { size: 15; text: "find bt device(s)"; onClicked: cmd.init_bt() }

    }


        Row {
            id:header
            anchors.margins: 10
            Repeater {
                model: sets
                delegate: Tab { tabs: sets }
            }
        }

        Rectangle {
            id: stack;
            color: "#e3e3e3"
            //z: -1
                        //anchors.fill: parent;
            //anchors.top: header.bottom; //anchors.left:
            height: tabWidget.height; width: tabWidget.width

            Column {
                anchors.left: parent.left
                 anchors.leftMargin: 10
                 spacing: 10
                Row { spacing: 10

                    Slider { id: finals_num }


                Btn { size: 15
                    text: "FINALS"
                    onClicked: {
                        for(var i=0; i<finals.children.length; i++)
                            if(finals.children[i].id=="finals_"+current)
                                finals.children[i].destroy()
                        cmd.begin_finals(sets[current], parseInt(finals_num.val));
                            //console.log('beginnnig')
                    }
                }

                Btn { size: 15; text: "next round";
                    onClicked: {
                        //console.log(sets[current])
                        var c_races=String(cmd.next_round(sets[current])).split('\r\n')
                        for(var i=0; i<c_races.length; i++)
                            c_races[i]=c_races[i].split(/[ ]*vs[ ]*/)

                        //c_races.shift()

                        //console.log(c_races)
                        var comp=Qt.createComponent('Round.qml')
                        var obj=comp.createObject(finals)
                        obj.id="finals_"+current
                        //obj.x=100*current
                        obj.races=c_races

                    }

                }
                Btn {
                    property bool showing_res: false
                    size: 15; text: showing_res ? "stop show" : "show results";
                    onClicked: {
                        if(showing_res)
                            cmd.abort()
                        else
                            cmd.show_results(sets[current], 0, 5)

                        showing_res = !showing_res
                    }

                }

                }

            Row {

                Rectangle {

                width: 200
                height:tabWidget.height-header.height
                color: "white"
            ListView {
                clip: true
                x: 10
                //interactive: false
                header: Rectangle { color: "black"; height: 10; width: parent.width  }
                footer: Rectangle { color: "black" ; height: 10; width: parent.width  }
                anchors.fill: parent
                //anchors.fill: parent
                model: best_times[current]
                delegate:  Text {

                    height: 30;
                    text: modelData

                    MouseArea {
                        anchors.fill: parent
                        drag.target: parent
                        drag.axis: Drag.XandYAxis

                        onPressed: { drag.target.z=1 }

                    }
                }
            }
                }

            Row { id: finals; height: 640; width: 20 }


            }
        }
    }


    }
}
