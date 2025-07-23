<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output indent="yes" method="html"/>
	<xsl:template match="FILMS">
<table width="70%" align="center" border="1">
	
		<tr bgcolor="yellow"  >
			<th>			Titre			</th>
			<th>			Année			</th>
			<th>			Genre			</th>

		</tr>
		<xsl:for-each select="FILM">
		<xsl:sort select="@Annee" order="descending"/>
		<xsl:if test="GENRE='Drame'">
		<tr  >
			<td>			<xsl:value-of select="TITRE"/>			</td>
			<td> 		    <xsl:value-of select="@Annee"/>			</td>
			<td >			<xsl:value-of select="GENRE"/>			</td>
		</tr>
		</xsl:if>
		</xsl:for-each>

</table>


</xsl:template>
</xsl:stylesheet>
