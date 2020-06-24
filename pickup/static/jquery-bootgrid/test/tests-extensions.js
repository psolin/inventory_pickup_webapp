/*jshint -W024 */
/*jshint -W117 */

QUnit.module("extensions");

QUnit.test("String.resolve basic (one dimension) test", function ( assert )
{
    assert.expect( 1 );

    // given
    var values = {
            first: "test",
            second: "case"
        },
        stringToResolve = "{{first}} {{second}}";

    // when
    var result = stringToResolve.resolve(values);

    // then
    assert.equal(result, "test case", "Valid string");
});

QUnit.test("String.resolve advanced (n dimension) test", function ( assert )
{
    assert.expect( 1 );

    // given
    var values = {
            first: {
                sub: "this is"
            },
            second: "a",
            third: {
                more: "more",
                adv: {
                    test: "advanced test"
                },
                "case": "case"
            }
        },
        stringToResolve = "{{first.sub}} {{second}} {{third.more}} {{third.adv.test}} {{third.case}}";

    // when
    var result = stringToResolve.resolve(values);

    // then
    assert.equal(result, "this is a more advanced test case", "Valid string");
});