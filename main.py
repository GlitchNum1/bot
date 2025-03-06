import discord
import asyncio
from discord.ext import commands

TOKEN = "MTM0Njk1MzA3ODk4MDYwODIyMw.GlGAp-.JXSAzQLq7GINNC0MF1o-zVWjSoXrQTHJboO9jQ"

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)

# تخزين أسماء السيرفرات والمهام المرتبطة بها
server_names = {}
tasks = {}

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول كـ {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)  # السماح فقط للمشرفين
async def setname(ctx, *, name: str):
    """يحدد اسم السيرفر الذي سيتم التغيير إليه"""
    if len(name) < 2 or len(name) > 100:
        await ctx.send("❌ يجب أن يكون الاسم بين 2 و 100 حرف!")
        return
    
    server_names[ctx.guild.id] = name
    await ctx.send(f"✅ تم تعيين اسم السيرفر الجديد إلى: `{name}`")
    
    # إذا كان هناك بالفعل مهمة قيد التشغيل، نقوم بإلغائها أولاً
    if ctx.guild.id in tasks:
        tasks[ctx.guild.id].cancel()

    # تشغيل عملية تغيير الاسم في هذا السيرفر فقط
    task = asyncio.create_task(change_server_name(ctx.guild))
    tasks[ctx.guild.id] = task

async def change_server_name(guild):
    """يغير اسم السيرفر بشكل تدريجي حسب الاسم المحدد له"""
    await bot.wait_until_ready()
    
    while guild.id in server_names:
        server_name = server_names[guild.id]
        
        for i in range(2, len(server_name) + 1):
            new_name = server_name[:i]
            try:
                await guild.edit(name=new_name)
            except discord.errors.Forbidden:
                print(f"❌ لا أملك صلاحية تغيير اسم السيرفر في: {guild.name}")
                return
            except discord.errors.HTTPException as e:
                print(f"⚠️ خطأ أثناء تغيير اسم السيرفر ({guild.name}): {e}")
                return
            
            await asyncio.sleep(2)  # انتظار بين كل تغيير
        
        await asyncio.sleep(5)  # انتظار قبل إعادة التكرار

# التعامل مع خطأ عدم امتلاك الصلاحيات
@setname.error
async def setname_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ هذا الأمر متاح فقط للمشرفين!")

bot.run(TOKEN)
