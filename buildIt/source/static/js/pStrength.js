var check = document.getElementById("check")
var user = document.getElementById("username")
var pass = document.getElementById("password")
var repass = document.getElementById("password_confirm")
var inputs = document.getElementsByTagName("input")
// var regbutton = document.getElementsByTagName("button")[0]
var colors = [
    "#ff4757",
    "#ffa502",
    "#2ed573",
    "#00ced1"
    
]

function checksame(){
    // 判断条件为如果两个密码输入框的内容一致且密码长度大于0，则边框设置为绿色
    if(pass.value == repass.value && pass.value.length >0){
        pass.style.border = repass.style.border = "1px solid #7bed9f"
        return true
    }
    else if(pass.value != repass.value && pass.value.length >0){
        pass.style.border = repass.style.border = "1px solid #ff6b81"
        return false
    }
    else{
        // 如果密码长度为0，则边框颜色为白色
        pass.style.border = repass.style.border = "1px solid white"
        return false
    }
}

function checkpass(val){
    var sl = 0
    var c1 = /[a-z]/
    var c2 = /[0-9]/
    var c3 = /[A-Z]/
    var c4 = /[\x21-\x2f\x3a-\x40\x5b-\x60\x7B-\x7F]/
    if(c1.test(val)){
        sl++
    }
    if(c2.test(val)){
        sl++
    }
    if(c3.test(val)){
        sl++
    }
    if(c4.test(val)){
        sl++
    }
    return (sl)
 }


 for(var i=0 ; i < inputs.length; i++){
    console.log(inputs.length)
    // window.alert('弹出窗口调试');
    inputs[i].addEventListener("keyup", function(){
        var level = checkpass(pass.value)
        for(var i=0; i < 4; i++){
            if(i < level){
                check.children[i].style.background=colors[i]
            }
            else{
                check.children[i].style.background="black"
            }
        }
        // // 综合结果判断是否需要电量注册按钮
        // if(checksame() && pass.value.length>7 && level>2 && user.value.length >0){
        //     regbutton.style.color="white"
        //     regbutton.style.border = "1px solid white"
        //     regbutton.style.cursor = "pointer"
        // }
        // else{
        //     regbutton .style.color = "gray"
        //     regbutton.style.border = "1px solid gray"
        //     regbutton.style.cursor = "default"
        // }

        

    })
 }