import pagination as pages
async def page(ctx, embeds):
  if len(embeds) != 1:
    paginator = pages.Paginator(pages=embeds, show_disabled=True, show_indicator=True)
    return await paginator.send(ctx)
  else:
    await ctx.send(embeds=embeds) 