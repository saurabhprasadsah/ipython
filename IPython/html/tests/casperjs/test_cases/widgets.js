//
// Test the widget framework.
//
casper.notebook_test(function () {
    //this.test.begin("widget tests (notebook)", 2, function(test) {


    // Utility function that allows us to easily execute a cell of python code
    // and wait for the results.
    var that = this;
    var run_python_code = function(code){
        var index = that.evaluate(function (code) {
            var index = IPython.notebook.ncells();
            var cell = IPython.notebook.insert_cell_at_index('code', index);
            cell.set_text(code);
            cell.execute();
            return index;
        }, code);

        that.wait_for_output(index);
        return index;
    };

    // Test widget dependencies ////////////////////////////////////////////////
    run_python_code('from IPython.html import widgets\n' + 
                    'from IPython.display import display, clear_output\n' + 
                    'widgets.init_widget_js()');
    this.wait(500); // Wait for require.js async callbacks to load dependencies.
    
    this.then(function () {
    
        // Check if the WidgetManager class is defined.
        this.test.assert(this.evaluate(function() {
            return IPython.WidgetManager != undefined; 
        }), 'WidgetManager class is defined');
    
        // Check if the widget manager has been instanciated.
        this.test.assert(this.evaluate(function() {
            return IPython.notebook.widget_manager != undefined; 
        }), 'Notebook widget manager instanciated');
    });


    // Check widget mapping ////////////////////////////////////////////////////
    var cell_index = run_python_code('names = [name for name in dir(widgets)' + 
        ' if name.endswith("Widget") and name!= "Widget"]\n' +
        'for name in names:\n' +
        '    print(name)\n');

    this.then(function () {
        // Get the widget names that are registered with the widget manager.  Assume
        // a 1 to 1 mapping of model and widgets names (model names just have 'model'
        // suffixed).
        var javascript_names = this.evaluate(function () {
            names = [];
            for (var name in IPython.notebook.widget_manager.widget_model_types) {
                names.push(name.replace('Model',''));
            }
            return names;
        });

        // Get the widget names registered in python.
        var python_names = this.get_output_cell(cell_index).text.split('\n');

        // Make sure the two lists have the same items.
        for (var i in javascript_names) {
            var javascript_name = javascript_names[i];
            var found = false;
            for (var j in python_names) {
                var python_name = python_names[j];
                if (python_name==javascript_name) {
                    found = true;
                    break;
                }
            }
            this.test.assert(found, javascript_name + ' exists in python');
        }
        for (var i in python_names) {
            var python_name = python_names[i];
            if (python_name.length > 0) {
                var found = false;
                for (var j in javascript_names) {
                    var javascript_name = javascript_names[j];
                    if (python_name==javascript_name) {
                        found = true;
                        break;
                    }
                }
                this.test.assert(found, python_name + ' exists in javascript');
            }
        }
    });


    //}); // end of test.begin
});

