function FileuploadUI(file){
	this.file = file;
	this.json = "";
	this.filemun = 0;
	//this.fileJson = function(jarrKey){ return "\"photokey\":["+jarrKey+"]"};
	//---------------上传元素--------------
    this.uploadAreaElment = $("div[data-ariapannel=\"uploadarea\"]");
    this.uploader = "<div class='col-sm-3 show-upload' data-imgname="+file.id+"><div class='ui-post-upload uploadimg'><a href='#'> <div class='btn btn-shadow case-in zoom-img' style='display:none;'>浏览大图</div></a><div class = 'btn btn-shadow case-in progress-img' style ='display:none;'></div> <div class='del-bg'><button type='button' class='btn-del case-in'title='删除'><spanaria-hidden='true'>&times;</span></button></div></div></div>";

    this.imgBg = ".uploadimg"
    this.uploaderElment = ".show-upload";
    this.progressStatusElement = ".progress-img";
    this.showPictureElement = '.zoom-img';
    this.delPictureElement = '.btn-del';

    this.submit = $("[name=\"submit\"]")
}

//-------------上传ui---------------

FileuploadUI.prototype.imgStatus = function(isUploading,tip) {
	var file = this.file;
	$("div[data-imgname="+file.id+"]").find(this.progressStatusElement).attr("style","display:block;");
    if (isUploading) {
    	
        $("div[data-imgname="+file.id+"]").find(this.progressStatusElement).text("上传中...");//.height(file.loaded + "%")
    } else $("div[data-imgname="+file.id+"]").find(this.progressStatusElement).text(tip);
};
FileuploadUI.prototype.bindUploadCancel = function(up) {
	var self = this;
	$(this.delPictureElement).click(function(){
		if (up) {
        up.removeFile(self.file);
        $("div[data-imgname=\""+self.file.id+"\"]").remove();
    	self.filemun;
    	}
	})
};
FileuploadUI.prototype.crateImg = function() {
    if(this.filemun !=10) this.uploadAreaElment.append(this.uploader);
    else {
    	var ui = new UI();
		ui.modalShow(function(){
			//$(".modal-body").attr("style","background-image:url("+url+");height:600px;");
			$(".modal-body").text("已达到上限")//append("<img src="+url+" width:890 >");
			$(".modal").modal('show');
		},0,0)
    }
};
FileuploadUI.prototype.getJson = function(){
	var self = this;
	var a;
	self.submit.click(function(){
		a = $("div[data-imgname]").length;
		self.json += "\"photokey\":[";
		$("div[data-imgname]").each(function(index){
			self.json += "{\"key\":\""+$(this).attr("data-imgname")+"\"}";
			if (index != a-1) self.json +=",";
		});
		self.json += "]";
		
		//self.fileJson("{\"key\":\""+key+"\"},");
		$(".imgjson").attr("value",self.json);
	});
	
	
};
//FileuploadUI.prototype.fileJson = function(jarrKey){ return "\"photokey\":["+jarrKey+"]"};
FileuploadUI.prototype.eachUpload = function(url,key){
	var file = this.file;
	var self = this;
	$("div[data-imgname="+file.id+"]").find(this.imgBg).attr("style","background-image:url("+url+")").hover(function() {
        $(this).find(self.showPictureElement).toggle()

    });
	$("div[data-imgname="+file.id+"]").find(this.showPictureElement).click(function(){
		var ui = new UI();
		ui.modalShow(function(){
			//$(".modal-body").attr("style","background-image:url("+url+");height:600px;");
			$(".modal-body").append("<img src="+url+" width:890 >");
			$(".modal").modal('show');
		},1,1)
	});//closest("a").attr("href",url)
	$("div[data-imgname="+file.id+"]").find(this.progressStatusElement).attr("style","display:none;");
};