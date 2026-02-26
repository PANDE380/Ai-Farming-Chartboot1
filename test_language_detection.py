from app import chat, auto_lang

print("detect french:", auto_lang('bonjour je suis agriculteur'))
print("detect arabic:", auto_lang('مرحبا كيف الحال'))
print("detect hindi:", auto_lang('नमस्ते मुझे मदद चाहिए'))
print("chat french reply:", chat(req=type('r',(),{'message':'bonjour','language':'auto'})()))
print("chat arabic hello:", chat(req=type('r',(),{'message':'مرحبا','language':'auto'})()))
print("chat hindi hello:", chat(req=type('r',(),{'message':'नमस्ते','language':'auto'})()))
