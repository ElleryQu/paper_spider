$(container).find("dd").click(function () {
    $(container).find("li").removeClass(parentCurClass);
    $(container).find("dd").removeClass(childCurClass);
    $(this).parents("li").addClass(parentCurClass);
    $(this).addClass(childCurClass);

    curDate = $(this).find("a").attr("value");
    curDateTemp = $(this).find("a").html();
    $(listBoxDate).html(curDateTemp);
    NPaperDetail.NpaperXsltByDate(curDate);
});

npaperDetail.NpaperXsltByDate = function (date, pageIndex) {
    var json = {};
    json.pcode = $("#pCode").val();
    json.py = $("#bzpym").val();
    json.pageIndex = pageIndex > 0 ? pageIndex + 1 : 1;//第几页；//jquery分页插件从0开始；后台返回数据分页从1开始，此值为分页页码，所以传入后台加1
    json.pageSize = 20;//页面条数
    json.date = date;
    if (pageIndex != undefined) {
        $('html, body').animate({
            scrollTop: $(".journalTabbox").offset().top
        }, 10);
    }
    $("#articleData").html("正在加载数据...");
    $.post(AppPath + "/newspapers/date/articles", json, function (html) {
        $("#articleData").html(html);

        $("#partiallistcurrent").html($("#pageIndex").val());
        $("#partiallistcount2").html($("#pageCount").val());
        $("#partiallistcount").html($("#maxCount").val());

        setPageInfo($("#pageIndex").val(), $("#pageCount").val());

        //if ($("#rightCatalog").find(".pagebox").children().length == 0) {//仅初次加载
        rightPager($("#maxCount").val(), pagerByDate, true, pageIndex);
        //}

    });
};

AppPath = "/" + "knavi";

//  https://navi.cnki.net//knavi/newspapers/date/articles
AppPath = "http://124.16.81.62/https/77726476706e69737468656265737421fef657956933665b774687a98c/knavi"

var json = {};
json.pcode = $("#pCode").val();
json.py = $("#bzpym").val();
json.year = "2021"
// json.pageIndex = 1
// json.pageSize = 20;//页面条数
// json.date = "2wa1vw8q_b1KATP3BQYGGgizcFMndnfduiKJqgcwa7Y_wwMpUpcXTmUd1_vNIawzm4cFKemdyX8=";

$.post(AppPath + "/newspapers/data/group", json)
// $.post(AppPath + "/newspapers/date/articles", json)