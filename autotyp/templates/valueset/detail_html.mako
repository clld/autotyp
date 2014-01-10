<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>${_('Value Set')} ${h.link(request, ctx.language)}/${h.link(request, ctx.parameter)}</h2>

<h3>${_('Values')}</h3>
<table class="table table-hover table-nonfluid">
% for i, value in enumerate(ctx.values):
    % if i == 0:
    <thead>
        <tr>
            <th> </th>
            % for d in value.data:
            <th>${d.key}</th>
            % endfor
        </tr>
    </thead>
    <tbody>
    % endif
        <tr>
            <td class="right">${i + 1}</td>
            % for d in value.data:
            <td>${d.value}</td>
            % endfor
        </tr>
% endfor
    </tbody>
</table>

<%def name="sidebar()">
<div class="well well-small">
<dl>
    ##<dt class="contribution">${_('Contribution')}:</dt>
    ##<dd class="contribution">
    ##    ${h.link(request, ctx.contribution)}
    ##    by
    ##    ${h.linked_contributors(request, ctx.contribution)}
    ##    ${h.button('cite', onclick=h.JSModal.show(ctx.contribution.name, request.resource_url(ctx.contribution, ext='md.html')))}
    ##</dd>
    <dt class="language">${_('Language')}:</dt>
    <dd class="language">${h.link(request, ctx.language)}</dd>
    <dt class="parameter">${_('Parameter')}:</dt>
    <dd class="parameter">${h.link(request, ctx.parameter)}</dd>
    % if ctx.references or ctx.source:
    <dt class="source">${_('Source')}:</dt>
        % if ctx.source:
        <dd>${ctx.source}</dd>
        % endif
        % if ctx.references:
        <dd class="source">${h.linked_references(request, ctx)|n}</dd>
        % endif
    % endif
    ${util.data(ctx, with_dl=False)}
</dl>
</div>
</%def>
