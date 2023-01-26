// When the user scrolls down 20px from the top of the document, slide down the navbar
// When the user scrolls to the top of the page, slide up the navbar (50px out of the top view)
window.onscroll = function () { scrollFunction() };


//TODO figirue out how to dynamically specify when to show the navbar (instead of fixing it)
function scrollFunction() {
    if (document.getElementById("filter-navbar") == null) {     //some pages do not load with filter-navbar
        return
    }

    let reveal_navbar_height = window.innerHeight*.5;
    let navbar_height = document.getElementsByClassName("navbar")[0].offsetHeight - 2;

    if (document.body.scrollTop > reveal_navbar_height || document.documentElement.scrollTop > reveal_navbar_height|| document.getElementById("offcanvas") != null) {
        document.getElementById("filter-navbar").style.top = navbar_height.toString() + "px";
    }
    else {
        document.getElementById("filter-navbar").style.top = "-" + navbar_height.toString() + "px";
    }
} 