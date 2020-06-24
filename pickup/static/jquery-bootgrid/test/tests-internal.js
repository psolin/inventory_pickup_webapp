/*jshint -W024 */
/*jshint -W117 */

QUnit.module("internal functions", {
    beforeEach: function ()
    {
        $("#qunit-fixture").html("<table id=\"test\"><thead><tr><th data-column-id=\"id\"></th></tr></thead><tfoot><tr><td></td></tr></tfoot></table>");
    },
    afterEach: function ()
    {
        $("#qunit-fixture").empty();
    }
});

QUnit.test("findFooterAndHeaderItems test", function ( assert )
{
    assert.expect( 1 );

    // given
    var instance = {
        footer: $("#test > tfoot"),
        header: $("#test > thead")
    };
    var selector = "tr";

    // when
    var result = findFooterAndHeaderItems.call(instance, selector);

    // then
    assert.equal(result.length, 2, "Found two elements as expected");
});

QUnit.test("findFooterAndHeaderItems test (footer is null)", function ( assert )
{
    assert.expect( 1 );

    // given
    var instance = {
        footer: null,
        header: $("#test > thead")
    };
    var selector = "tr";

    // when
    var result = findFooterAndHeaderItems.call(instance, selector);

    // then
    assert.equal(result.length, 1, "Found one element as expected");
});

QUnit.test("findFooterAndHeaderItems test (header is null)", function ( assert )
{
    assert.expect( 1 );

    // given
    var instance = {
        footer: $("#test > tfoot"),
        header: null
    };
    var selector = "tr";

    // when
    var result = findFooterAndHeaderItems.call(instance, selector);

    // then
    assert.equal(result.length, 1, "Found one element as expected");
});

QUnit.test("findFooterAndHeaderItems test (footer and header is string empty)", function ( assert )
{
    assert.expect( 2 );

    // given
    var instance = {
        footer: "",
        header: ""
    };
    var selector = "tr";

    // when
    var result = findFooterAndHeaderItems.call(instance, selector);

    // then
    assert.equal(result.length, 0, "Found one element as expected");
    assert.ok(result.find, "Got an empty jQuery array as expected");
});

QUnit.test("findFooterAndHeaderItems test (footer and header is null)", function ( assert )
{
    assert.expect( 2 );

    // given
    var instance = {
        footer: null,
        header: null
    };
    var selector = "tr";

    // when
    var result = findFooterAndHeaderItems.call(instance, selector);

    // then
    assert.equal(result.length, 0, "Found no elements as expected");
    assert.ok(result.find, "Got an empty jQuery array as expected");
});

QUnit.test("getRequest post function test", function ( assert )
{
    assert.expect( 1 );

    // given
    var instance = {
            options: {
                post: function()
                {
                    return {
                        id: "test"
                    };
                },
                requestHandler: function (request) { return request; }
            },
            current: 1,
            rowCount: 5,
            sortDictionary: [],
            searchPhrase: ""
        },
        expected = {
            current: 1,
            id: "test",
            rowCount: 5,
            sort: [],
            searchPhrase: ""
        };

    // when
    var result = getRequest.call(instance);

    // then
    assert.propEqual(result, expected, "Valid request object");
});

QUnit.test("getRequest post object test", function( assert ) {
    assert.expect( 1 );

    // given
    var instance = {
            options: {
                post: {
                    id: "test"
                },
                requestHandler: function (request) { return request; }
            },
            current: 1,
            rowCount: 5,
            sortDictionary: [],
            searchPhrase: ""
        },
        expected = {
            current: 1,
            id: "test",
            rowCount: 5,
            sort: [],
            searchPhrase: ""
        };

    // when
    var result = getRequest.call(instance);

    // then
    assert.propEqual(result, expected, "Valid request object");
});

QUnit.test("getCssSelector test", function ( assert )
{
    assert.expect( 1 );

    // given
    var classNames = "       itallic bold  normal   ";

    // when
    var result = getCssSelector(classNames);

    // then
    assert.equal(result, ".itallic.bold.normal", "Valid css selector");
});

QUnit.test("getUrl function test", function ( assert )
{
    assert.expect( 1 );

    // given
    var instance = {
        options: {
            url: function()
            {
                return "url/test/1";
            }
        }
    };

    // when
    var result = getUrl.call(instance);

    // then
    assert.equal(result, "url/test/1", "Valid URL");
});

QUnit.test("getUrl string test", function ( assert )
{
    assert.expect( 1 );

    // given
    var instance = {
        options: {
            url: "url/test/1"
        }
    };

    // when
    var result = getUrl.call(instance);

    // then
    assert.equal(result, "url/test/1", "Valid URL");
});
