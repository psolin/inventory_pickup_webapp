/*jshint -W024 */
/*jshint -W117 */

QUnit.module("render functions", {
    beforeEach: function ()
    {
        $("#qunit-fixture").html("<div id=\"header\"><div class=\"infos\"></div></div><div id=\"table\"></div><div id=\"footer\"><div class=\"infos\"></div></div>");
    },
    afterEach: function ()
    {
        $("#qunit-fixture").empty();
    }
});

function renderInfosTest(expected, message, current, rowCount, total, assert)
{
    // given
    var instance = {
            element: $("#table").data(namespace, {
                header: header,
                footer: footer
            }),
            options: {
                navigation: 1,
                css: {
                    infos: "infos"
                },
                templates: {
                    infos: "<div class=\"infos\">{{ctx.start}}{{ctx.end}}{{ctx.total}}</div>"
                }
            },
            current: current,
            rowCount: rowCount,
            total: total,
            header: $("#header"),
            footer: $("#footer")
        };

    // when
    renderInfos.call(instance);

    // then
    var infos = instance.header.find(".infos").text();
    assert.equal(infos, expected, message);
}

QUnit.test("renderInfos all test", function ( assert )
{
    assert.expect( 1 );

    renderInfosTest("11010", "Valid infos", 1, -1, 10, assert);
});

QUnit.test("renderInfos paged test", function ( assert )
{
    assert.expect( 1 );

    renderInfosTest("1510", "Valid infos", 1, 5, 10, assert);
});