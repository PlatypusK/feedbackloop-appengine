/**A reporter that stores the current coverage data in a global variable which must be defined in the qunit_composite test runner
*A global list variable named coverageList must be defined in the qunit-composite test_suite
*
*/
(function (){
	
	function getCover(filename,data){
		var ret = {
            coverage: 0,
            hits: 0,
            misses: 0,
            sloc: 0
        };
        for (var i = 0; i < data.source.length; i++) {
            var line = data.source[i];
            var num = i + 1;
            if (data[num] === 0) {
                ret.misses++;
                ret.sloc++;
            } else if (data[num] !== undefined) {
                ret.hits++;
                ret.sloc++;
            }
        }
        ret.coverage = ret.hits / ret.sloc * 100;

        return [filename,ret.hits,ret.sloc, 'Coverage: '+ ret.coverage+'%\n'];

    };
	
		
    blanket.customReporter= function(cov){
		var s=cov.files;
		var sortedFileNames = [];
		for(var name in cov.files){
				console.log(cov.files[name])
				data=cov.files[name];
				if(parent.coverageList!=undefined){
					parent.coverageList.push(getCover(name,data))
				}
				else{
					console.log(getCover(name,data))
				}
			}
        console.log(cov);
		console.log(s['http://localhost:8800/user_main.js'])
		console.log(cov.files)
    };
})();