

function findObjectInArray(array, key, value) {
    var obj = null;
    for(var i = 0, l = array.length; i < l && !obj; i++)
    {
        if(array[i][key] && array[i][key] === value)
        {
            obj = array[i];
        }
    }
    return obj;
}

function addProduct(array, object, key, value){
    // !! WARNING !! 
    // this function will MUTATE
    // both array and object

    // Search for an object by key=value
    // and increase the amount if found
    // otherwise just append it to array 
    // with amount equals one

    var obj = null;
    if(!!key && !!value)
    {
        obj = findObjectInArray(array, key, value);
    }

    if(obj)
    {
        obj.amount++;
        obj.total = obj.amount * obj.price;
    }
    else
    {
        object.amount = 1;
        object.total = object.price;
        array.push(object);
    }
    
}

function getProductsTotalCount(products) {
    products.forEach(function(item){
        console.log(item)
    })
}

var Product = React.createClass({
    getInitialState: function(){
        return {
            name: null,
            amount: 0,
            total: 0,
            price: 0
        }
    },
    render: function(){
        return (
            <tr>
                <td>
                    {this.props.name}
                </td>
                <td className="text-center">
                   {this.props.amount}
                </td>
                <td className="text-center">{this.props.price}</td>
                <td className="text-center">{this.props.total}</td>
                <td className="text-center">
                    <a href="#"><i className="fa fa-times"></i></a>
                </td>
            </tr>
        )
    }
})

var Cart = React.createClass({
    getInitialState: function(){
        return {
            products: []
        }
    },
    addProductToCart: function(id){
        this.props.transport.product(id, function(response){
            var products = this.state.products.slice();
            addProduct(products, response, "id", parseInt(id, 10));
            this.setState({
                products: products
            }, function(){
                document.getElementById('cart-total').innerHTML = getProductsTotalCount(this.state.products);
            });
        }.bind(this));
    },
    componentDidMount: function(){
        this.props.emitter.on('product-added', this.addProductToCart)
    },
    render: function(){
        
        var products = [];
        this.state.products.forEach(function(product){
            products.push(<Product {...product} key={product.id} />)
        });

        return (
            <div >
                <table className="table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Amount</th>
                                <th>Price</th>
                                <th>Total</th>
                                <th>
                                    <i className="fa fa-trash"></i>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {products}
                        </tbody>
                    </table>
                    <div className="cart-footer">
                        <button className="btn btn-primary">Checkout</button>
                    </div>
                </div>
        )
    }
});

module.exports = Cart;