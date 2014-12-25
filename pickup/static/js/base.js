$('.datepicker').pickadate({
    format: 'dddd, mmm. d, yyyy',
    formatSubmit: 'yyyy-mm-dd',
    today: '',
    clear: 'Clear',
    hiddenPrefix: 'prefix__',
    hiddenSuffix: '__suffix',
    hiddenName: true
});

$('[data-role="tagsinput"]').tagsinput({
  allowDuplicates: true
});