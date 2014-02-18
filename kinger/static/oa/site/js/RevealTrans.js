
var isIE = (document.all) ? true : false;

var $ = function (id) {
	return "string" == typeof id ? document.getElementById(id) : id;
};

var Class = {
	create: function() {
		return function() { this.initialize.apply(this, arguments); }
	}
}

var Extend = function(destination, source) {
	for (var property in source) {
		destination[property] = source[property];
	}
}

var Bind = function(object, fun) {
	return function() {
		return fun.apply(object, arguments);
	}
}

var Each = function(list, fun){
	for (var i = 0, len = list.length; i < len; i++) { fun(list[i], i); }
};


//ie only
var RevealTrans = Class.create();
RevealTrans.prototype = {
  initialize: function(container, options) {
	this._img = document.createElement("img");
	this._a = document.createElement("a");
	
	this._timer = null;//计时器
	this.Index = 0;//显示索引
	this._onIndex = -1;//当前索引
	
	this.SetOptions(options);
	
	this.Auto = !!this.options.Auto;
	this.Pause = Math.abs(this.options.Pause);
	this.Duration = Math.abs(this.options.Duration);
	this.Transition = parseInt(this.options.Transition);
	this.List = this.options.List;
	this.onShow = this.options.onShow;
	
	//初始化显示区域
	this._img.style.visibility = "hidden";//第一次变换时不显示红x图
	this._img.style.width = this._img.style.height = "100%"; this._img.style.border = 0;
	this._img.onmouseover = Bind(this, this.Stop);
	this._img.onmouseout = Bind(this, this.Start);
	isIE && (this._img.style.filter = "revealTrans()");
	
	this._a.target = "_blank";
	
	$(container).appendChild(this._a).appendChild(this._img);
  },
  //设置默认属性
  SetOptions: function(options) {
	this.options = {//默认值
		Auto:		true,//是否自动切换
		Pause:		1000,//停顿时间(微妙)
		Duration:	1,//变换持续时间(秒)
		Transition:	23,//变换效果(23为随机)
		List:		[],//数据集合,如果这里不设置可以用Add方法添加
		onShow:		function(){}//变换时执行
	};
	Extend(this.options, options || {});
  },
  Start: function() {
	clearTimeout(this._timer);
	//如果没有数据就返回
	if(!this.List.length) return;
	//修正Index
	if(this.Index < 0 || this.Index >= this.List.length){ this.Index = 0; }
	//如果当前索引不是显示索引就设置显示
	if(this._onIndex != this.Index){ this._onIndex = this.Index; this.Show(this.List[this.Index]); }
	//如果要自动切换
	if(this.Auto){
		this._timer = setTimeout(Bind(this, function(){ this.Index++; this.Start(); }), this.Duration * 1000 + this.Pause);
	}
  },
  //显示
  Show: function(list) {
	if(isIE){
		//设置变换参数
		with(this._img.filters.revealTrans){
			Transition = this.Transition; Duration = this.Duration; apply(); play();
		}
	}
	this._img.style.visibility = "";
	//设置图片属性
	this._img.src = list.img; this._img.alt = list.text;
	//设置链接
	!!list["url"] ? (this._a.href = list["url"]) : this._a.removeAttribute("href");
	//附加函数
	this.onShow();
  },
  //添加变换对象
  Add: function(sIimg, sText, sUrl) {
	this.List.push({ img: sIimg, text: sText, url: sUrl });
  },
  //停止
  Stop: function() {
	clearTimeout(this._timer);
  }
};
