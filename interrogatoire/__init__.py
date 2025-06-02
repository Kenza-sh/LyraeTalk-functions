import azure.functions as func
import logging
import json
def get_interro(type):
    if type=="N01US001":
      return["Avez-vous remarqué un creux, une bosse ou une touffe de poils en bas du dos de votre bébé ?","Avez-vous l’impression que votre bébé bouge moins les jambes par rapport aux bras ?"]
    elif type=="N01US002":
      return ["Avez-vous remarqué que la tête de votre bébé change de forme rapidement ?","Avez-vous déjà senti que la zone molle ou fontanelle sur la tête de votre bébé était gonflée ou tendue au toucher ?"]
    elif type=="N01US003":
      return ["Avez-vous ressenti de petites bosses dans votre cou ?","Avez-vous observé un gonflement dans votre cou?","Ressentez-vous une douleur dans votre cou?"]
    elif type=="N01US005":
      return ["Avez-vous constaté que l’avant de votre cou est plus gonflé qu’avant ?","Avez-vous l’impression d’avoir des difficultés à avaler vos aliments ou vos boissons ? ","Avez-vous remarqué que votre voix a changé?"]
    elif type=="N01US006":
      return ["Avez-vous ressenti une douleur vers l’oreille ou la joue, surtout au moment des repas ?","Avez-vous ressenti un gonflement vers l’oreille ou la joue ?"," Avez-vous remarqué que vous salivez moins ou que vous avez la bouche sèche ?"]
    elif type=="N01US007":
      return ["Avez-vous remarqué une petite bosse ou un gonflement sous votre menton ?","Ressentez-vous une douleur sous votre menton ou le long de votre mâchoire ?"]
    elif type=="N01US008":
      return ["Avez-vous senti une boule ou un durcissement dans votre sein quand vous le touchez ?"," Avez-vous une douleur inhabituelle dans un ou deux seins ?","Avez-vous remarqué un écoulement de liquide au niveau du mamelon ?"]
    elif type =="N01US009" :
      return ["Avez-vous remarqué une bosse ou un gonflement sous la peau, à un endroit précis ?","Ressentez-vous une douleur ou une gêne quand vous touchez cette bosse ou quand vous bougez ?","Avez-vous remarqué que la peau est plus rouge ou plus chaude à l’endroit de la masse ou du gonflement ?"]
    elif type=="N01US010":
      ["Ressentez-vous une douleur au ventre , si oui De quel côté ressentez-vous cette douleur au ventre ?","Avez-vous des vomissements ou des problèmes de transit intestinal ?","Avez-vous constaté que vous allez uriner plus souvent ?"]
    elif type=="N01US011":
      return ["Ressentez-vous une douleur au ventre ? si oui Ressentez-vous une douleur au ventre ?","Avez-vous des vomissements ou des problèmes de transit intestinal ? ","Avez-vous constaté que vous allez uriner plus souvent ?"]
    elif type=="N01US012":
      return["Avez-vous remarqué une bosse ou un gonflement sur votre ventre qui apparaît ou qui devient plus visible quand vous toussez ou faites un effort ?"," Ressentez-vous une douleur lorsque vous appuyez sur certaines zones de votre ventre ?"]
    elif type=="N01US013":
      return ["Ressentez-vous une douleur dans le bas du dos ou sur les côtés ?","Avez-vous une gêne en urinant ?","Avez-vous constaté que vous allez uriner plus souvent ?","Avez-vous observé que la couleur de vos urines était rosée ou rouge ? "]
    elif type=="N01US014":
      return["Ressentez-vous une douleur sous vos côtes à droite ? ","Avez-vous remarqué que votre peau ou le blanc de vos yeux est devenu plus jaune que d’habitude ?"]
    elif type=="N01US015":
      return["Ressentez-vous une douleur sous vos côtes à droite?","Avez-vous remarqué que votre peau ou le blanc de vos yeux est devenu plus jaune que d’habitude ?"]
    elif type=="N01US016":
      return ["Avez-vous des difficultés à uriner?"," Vous levez-vous souvent la nuit pour aller aux toilettes ?","Avez-vous remarqué une coloration rose ou rouge dans vos urines ?"]
    elif type=="N01US017":
      return ["Ressentez-vous une douleur ou une gêne dans les testicules? "," Avez-vous remarqué une bosse, un gonflement de vos testicules ?"]
    elif type=="N01US018":
      return [" Avez-vous remarqué une bosse ou un gonflement dans la région de l’aine, surtout quand vous faites un effort ou que vous toussez ?","Ressentez-vous une douleur ou une gêne à l’aine lorsque vous marchez, vous penchez ou soulevez un objet ?"]
    elif type=="N01US020":
      return ["Ressentez-vous des douleurs ou des crampes dans le bas-ventre, en dehors de vos règles ?","Avez-vous remarqué des saignements ?"]
    elif type=="N01US021":
      return ["Avez-vous constaté que vous devez aller plus souvent aux toilettes ?","Ressentez-vous une difficulté lorsque vous essayez d’uriner ?"," Avez-vous déjà observé que vos urines étaient rosées ou rouge ? "]
    elif type=="N01US022":
      return ["Ressentez-vous une douleur dans la zone où votre rein a été greffé ?","Avez-vous remarqué que vous produisez moins d’urine que d’habitude? "," Avez-vous eu de la fièvre, des frissons ou des sueurs inhabituelles ces derniers temps ? "]
    elif type=="N01US023":
      return ["Avez-vous remarqué une douleur sous vos côtes à droite, là où se trouve votre foie greffé ? ","Avez-vous constaté que votre peau ou le blanc de vos yeux a pris une couleur jaune ? ","Avez-vous eu de la fièvre, des frissons ou des sueurs inhabituelles ces derniers temps ?"]
    elif type=="N01US024":
      return ["Avez-vous remarqué une bosse dans votre aisselle ?"," Ressentez-vous une douleur sous le bras ?","Avez-vous observé que votre aisselle est rouge ou plus chaude que d’habitude ?"]
    elif type=="N01US025":
      return [" Ressentez-vous une douleur dans l’épaule quand vous levez votre bras ou faites certains mouvements ?","Avez-vous remarqué que vous ne pouvez plus lever le bras aussi haut qu’avant ?"]
    elif type=="N01US026":
      return ["Ressentez-vous une douleur dans votre bras, entre l’épaule et le coude ?","Avez-vous remarqué une bosse ou un gonflement de votre bras ?","Avez-vous des sensations de picotements ou d’engourdissement dans votre bras ? "]
    elif type=="N01US027":
      return ["Ressentez-vous une douleur dans les articulations de votre main ou de vos doigts lorsque vous les bougez ?"," Avez-vous remarqué que certains de vos doigts sont gonflés?"]
    elif type=="N01US028":
      return ["Ressentez-vous une douleur de vos doigts quand vous les bougez ? ","Avez-vous parfois la sensation que votre doigt est engourdi ou que vous ressentez des picotements ?"]
    elif type=="N01US029":
      return [" Avez-vous une douleur au niveau de l’extérieur du coude ?","Avez-vous une douleur au niveau de l’intérieur du coude ? "," Avez-vous remarqué que vous ne pouvez plus plier votre coude comme avant ?"]
    elif type=="N01US030":
      return ["Ressentez-vous une douleur dans l’avant-bras quand vous faites un effort ou soulevez quelque chose ?","Avez-vous remarqué une bosse ou un gonflement inhabituel sur votre avant-bras ?","Avez-vous ressenti des picotements ou un engourdissement dans votre avant-bras?"]
    elif type=="N01US031":
      return ["Ressentez-vous une douleur au poignet ?"," Avez-vous remarqué que votre poignet est enflé ou plus épais que d’habitude ?"]
    elif type=="N01US034":
      return ["Avez-vous l’impression que votre cheville se dérobe ou “lâche” parfois quand vous marchez ?","Ressentez-vous une douleur lorsque vous bougez ou tournez votre cheville ?"," Avez-vous remarqué que votre cheville est souvent enflée ou plus grosse que d’habitude ?"]
    elif type=="N01US035":
      return ["Ressentez-vous une douleur dans votre cuisse, surtout après un effort ?"," Avez-vous remarqué une bosse ou un gonflement inhabituel sur votre cuisse ?"]
    elif type=="N01US036":
      return ["Ressentez-vous une douleur dans l’aine ou sur le côté de la hanche ?","Avez-vous remarqué que vous avez du mal à plier ou à faire pivoter votre hanche ?"," Avez-vous observé que vous boitez ou que vous ressentez une gêne en marchant ?"]
    elif type=="N01US038" :
      return ["Avez-vous une histoire de problème de hanche à la naissance dans la famille ?","Votre bébé pesait-il plus que 4KG à la naissance ?"]
    elif type=="N01US040":
      return ["Votre enfant se plaint-il d’une douleur dans l’aine ou sur le côté de la hanche lorsqu’il court ou joue ?","Avez-vous remarqué que votre enfant boîte ou marche d’une façon différente de d’habitude ?"]
    elif type=="N01US041":
      return ["Ressentez-vous une douleur quand vous appuyez sur votre genou ou quand vous le pliez ?"," Avez-vous remarqué que votre genou est plus enflé que d’habitude ?","Etes-vous gêné dans les escaliers ?"]
    elif type=="N01US042":
      return ["Avez-vous une douleur ?","Avez-vous remarqué que l’un de vos orteils est plus gonflé que les autres ?","Avez-vous parfois des fourmillements ou une sensation de pied “endormi” dans vos orteils ?"]
    elif type=="N01US043":
      return ["Avez-vous une douleur derrière la cheville quand vous touchez ou appuyez sur le tendon ?","Avez-vous remarqué que le tendon est plus épais ou gonflé par rapport à l’autre côté ? "]
    elif type=="N01US044":
      return ["Avez-vous ressenti une douleur vive ou un “coup” dans votre cuisse en faisant un mouvement brusque ou en courant ?"]
    elif type=="N01US009":
        return [" Avez-vous remarqué une bosse ou un gonflement sous la peau? ","Ressentez-vous une douleur quand vous touchez ou appuyez ?","Avez-vous remarqué que la peau est plus rouge ou plus chaude? "]
    elif type=="N01US045":
      return ["Avez-vous une douleur au mollet ? ","Avez-vous remarqué que l’un de vos mollets est plus gonflé ou plus gros que l’autre ?"]
    elif type=="N01RX001":
      return ["Ressentez-vous une douleur lorsque vous ouvrez ou fermez la bouche ? ","Ressentez-vous un blocage lorsque vous ouvrez ou fermez la bouche ?","Entendez-vous des bruits de craquement dans votre mâchoire quand vous mâchez ?"]
    elif type=="N01RX002":
      return [" Avez-vous une ou plusieurs dents qui vous font mal depuis un moment ?","Ressentez-vous une douleur ou un choc dans vos dents quand vous mangez ou buvez quelque chose de chaud ou de froid ? "]
    elif type=="N01RX003":
      return ["Avez-vous remarqué que vos dents ne s’emboîtent pas correctement quand vous fermez la bouche ?","Ressentez-vous une douleur dans la mâchoire quand vous mâchez ou serrez les dents ? "]
    elif type=="N01RX004":
      return ["Avez-vous le nez souvent bouché, vous empêchant de bien respirer ?","Ressentez-vous une pression ou une douleur au niveau du visage?"]
    elif type == "N01RX006":
        return [
            "Vous a-t-on fait remarquer que vous ronflez ?",
            "Ressentez-vous une sensation d’oreilles bouchées ?",
            "Avez-vous souvent des otites, rhumes ou angines qui reviennent fréquemment ?"
        ]
    elif type == "N01RX007":
        return [
            "Avez-vous peut-être des fragments de métal dans les yeux ?"
        ]
    elif type == "N01RX008":
        return [
            "Avez-vous remarqué que votre nez est tordu ?",
            "Avez-vous le nez bouché ?",
            "Avez-vous subi un choc ?"
        ]
    elif type == "N01RX012":
        return [
            "Fumez-vous, ou avez-vous fumé ?",
            "Avez-vous du mal à respirer ?",
            "Toussez-vous depuis plus de deux semaines ?",
            "Ressentez-vous une douleur dans la poitrine ?"
        ]
    elif type == "N01RX012":
        return [
            "Avez-vous une douleur au niveau des côtes, surtout lorsque vous appuyez dessus ou respirez profondément ?",
            "Avez-vous eu un choc ou une chute ?",
            "Avez-vous du mal à inspirer à fond à cause d’une douleur ?"
        ]
    elif type == "N01RX018":
        return [
            "Fumez-vous, ou avez-vous fumé ?",
            "Avez-vous du mal à respirer ?",
            "Avez-vous eu un choc ou une chute ?",
            "Ressentez-vous une douleur dans la poitrine ?"
        ]
    elif type == "N01RX019":
        return [
            "Avez-vous remarqué que vous avez du mal à avaler vos aliments ou vos boissons ?",
            "Avez-vous une sensation de brûlure, surtout après les repas ?",
            "Avez-vous parfois l’impression que la nourriture ou l’acide de l’estomac remonte dans votre gorge ?"
        ]
    elif type == "N01RX020":
        return [
            "Ressentez-vous des douleurs dans le haut du ventre, surtout après avoir mangé ?",
            "Avez-vous remarqué que vous avez du mal à avaler vos aliments ou vos boissons ?",
            "Avez-vous une sensation de brûlure, surtout après les repas ?",
            "Avez-vous parfois l’impression que la nourriture ou l’acide de l’estomac remonte dans votre gorge ?"
        ]
    elif type == "N01RX022":
        return [
            "Avez-vous une douleur au ventre ?",
            "Avez-vous remarqué que vous n’avez pas de gaz ni selles depuis un certain temps ?"
        ]
    elif type == "N01RX024":
        return [
            "Ressentez-vous des brûlures ou des douleurs quand vous urinez ?",
            "Avez-vous remarqué que vous allez uriner très souvent, même pour de petites quantités ?",
            "Avez-vous eu plusieurs infections urinaires au cours des derniers mois ?"
        ]
    elif type == "Cystographie Homme":
        return [
            "Avez-vous remarqué que votre jet d’urine est moins fort ou qu’il s’arrête parfois avant la fin ?",
            "Vous levez-vous souvent la nuit pour aller uriner ?",
            "Avez-vous l’impression de ne pas complètement vider votre vessie quand vous allez aux toilettes ?"
        ]
    elif type == "N01RX027":
        return [
            "Ressentez-vous une douleur dans la hanche ou au niveau de l’aine ?",
            "Avez-vous du mal à bouger votre hanche ou à faire certains mouvements (comme vous asseoir ou vous relever) ?",
            "Avez-vous remarqué que vous boitez ou qu’il vous est pénible de marcher longtemps ?"
        ]
    elif type == "N01RX031":
        return [
            "Ressentez-vous une douleur dans le bas du dos, sur le côté ?",
            "Avez-vous des difficultés à uriner ou remarquez-vous que vous y allez plus souvent qu’avant ?",
            "Avez-vous déjà eu des calculs rénaux (pierres aux reins) par le passé ?"
        ]
    elif type == "N01RX032":
        return [
            "Ressentez-vous une douleur dans la nuque ?",
            "Ressentez-vous une douleur qui descend parfois dans l’épaule ou le bras ?",
            "Avez-vous parfois l’impression que vos doigts picotent ou s’engourdissent ?"
        ]
    elif type == "N01RX037":
        return [
            "Ressentez-vous une douleur du haut du dos ?"
        ]
    elif type == "N01RX039":
        return [
            "Ressentez-vous des douleurs à plusieurs niveaux de la colonne, du cou jusqu’aux reins ?",
            "Avez-vous l’impression que tout votre dos est raide et que vous ne pouvez pas vous pencher facilement ?",
            "Avez-vous des sensations de décharges ou de picotements qui partent du dos et descendent dans vos bras ou vos jambes ?"
        ]
    elif type == "N01RX042":
        return [
            "Avez-vous des douleurs sur toute la colonne, de la nuque jusqu’au bas du dos ?",
            "Avez-vous remarqué que votre dos est courbé ou que vos épaules ne sont pas au même niveau ?",
            "Êtes-vous vite fatigué(e) ou ressentez-vous des douleurs après être resté(e) debout quelques minutes ?"
        ]
    elif type == "N01RX048":
        return [
            "Avez-vous une douleur entre les omoplates, surtout quand vous restez assis(e) longtemps ?",
            "Avez-vous parfois mal au milieu du dos quand vous prenez une grande inspiration ?",
            "Ressentez-vous que votre haut du dos est souvent tendu ou bloqué ?"
        ]
    elif type == "N01RX050":
        return [
            "Avez-vous une douleur qui se situe entre le milieu et le bas de votre dos ?",
            "Au lever, trouvez-vous que votre back est très raide, spécialement entre les côtes et les reins ?",
            "La douleur dans cette zone augmente-t-elle quand vous vous penchez en avant ou restez debout longtemps ?"
        ]
    elif type == "N01RX053":
        return [
            "Avez-vous une douleur dans le bas du dos qui vous empêche parfois de vous redresser facilement ?",
            "Ressentez-vous des élancements ou des picotements qui partent du bas du dos et descendent derrière la cuisse ou le mollet ?",
            "La douleur dans le bas du dos s’aggrave-t-elle quand vous restez longtemps assis(e) ?"
        ]
    elif type == "N01RX055":
        return [
            "Avez-vous une douleur dans le bas du dos qui se propage jusqu’à la hanche ou l’aine ?",
            "Avez-vous du mal à bouger la hanche, par exemple pour monter dans une voiture ou enfiler vos chaussures ?",
            "Avez-vous remarqué que vous boitez ou ressentez une gêne en marchant, surtout au niveau du bas du dos et de la hanche ?"
        ]
    elif type == "N01RX056":
        return [
            "Ressentez-vous une douleur au niveau du coccyx, surtout quand vous restez assis longtemps ?",
            "Avez-vous une gêne ou une douleur vive quand vous vous relevez d’une chaise ?",
            "Avez-vous déjà chuté sur les fesses ou reçu un coup au niveau du coccyx ?"
        ]
    elif type == "N01RX060":
        return [
            "Avez-vous du mal ou ressentez-vous une douleur quand vous tournez l’avant-bras (paume de la main vers le haut ou vers le bas) ?",
            "Avez-vous remarqué un gonflement inhabituel ou une bosse sur l’avant-bras ?",
            "Êtes-vous récemment tombé ou avez-vous reçu un coup sur l’avant-bras ?"
        ]
    elif type == "N01RX063":
        return [
            "Ressentez-vous une douleur quand vous levez le bras sur le côté (comme pour attraper quelque chose en hauteur) ?",
            "Avez-vous parfois l’impression que votre épaule sort de son emplacement ou se déboîte ?",
            "Entendez-vous ou ressentez-vous des craquements lorsque vous bougez votre épaule ?"
        ]
    elif type == "N01RX067":
        return [
            "Ressentez-vous une douleur ou une raideur quand vous pliez ou dépliez vos doigts ?",
            "Avez-vous remarqué une bosse ou une déformation à la base de votre pouce ou sur vos doigts ?",
            "Avez-vous des difficultés à attraper ou à tenir des objets en raison de douleurs ou de faiblesse dans la main ?"
        ]
    elif type == "N01RX063":
        return [
            "Avez-vous une douleur sur la partie supérieure de votre bras, entre l’épaule et le coude ?",
            "Avez-vous entendu un craquement ou ressenti une vive douleur après une chute sur le bras ?",
            "Avez-vous remarqué un gonflement ou un bleu important sur le bras depuis un choc ou une chute ?"
        ]
    elif type == "N01RX070":
        return [
            "Ressentez-vous une douleur à la face extérieure ou intérieure du coude, surtout quand vous soulevez un objet ?",
            "Avez-vous du mal à plier ou à redresser complètement votre coude ?",
            "Avez-vous remarqué que votre coude est gonflé ou rouge, surtout après un effort ou un choc ?"
        ]
    elif type == "N01RX072":
        return [
            "Ressentez-vous une douleur quand vous appuyez sur la base de votre pouce, entre le pouce et le poignet ?",
            "Le poignet vous semble-t-il instable, ou entendez-vous des craquements quand vous le bougez ?",
            "Avez-vous un gonflement ou une difficulté à plier et à redresser votre poignet complètement ?"
        ]
    elif type == "N01RX076":
        return [
            "Avez-vous remarqué que votre enfant est plus petit que les enfants de son âge ?",
            "Avez-vous constaté que les signes de puberté (pilosité, développement mammaire) apparaissent tardivement ou très tôt chez votre enfant ?",
            "Le médecin vous a-t-il déjà signalé un décalage entre l’âge réel et le développement des os de votre enfant ?"
        ]
    elif type == "N01RX078":
        return [
            "Votre cheville cède-t-elle ou se tord-elle facilement quand vous marchez ou courez ?",
            "Ressentez-vous une douleur au niveau de la cheville si vous appuyez dessus ou quand vous la faites pivoter ?",
            "Avez-vous remarqué que votre cheville est souvent enflée, surtout après une activité ou en fin de journée ?"
        ]
    elif type == "N01RX079":
        return [
            "Avez-vous une douleur sur la partie de la cuisse (entre la hanche et le genou) lorsque vous marchez ou êtes au repos ?",
            "Avez-vous du mal à porter le poids du corps sur cette jambe, par exemple quand vous vous levez d’une chaise ?",
            "Êtes-vous récemment tombé(e) ou avez-vous reçu un coup sur la cuisse ?"
        ]
    elif type == "N01RX028":
        return [
            "Ressentez-vous une douleur au niveau de la hanche, surtout quand vous marchez ou montez les escaliers ?",
            "Avez-vous remarqué que vous avez du mal à plier ou à tourner votre hanche ?",
            "Avez-vous remarqué que vous boitez ou ressentez une gêne en marchant ?"
        ]
    elif type == "N01RX082":
        return [
            "Ressentez-vous une douleur lancinante ou un élancement le long de votre tibia ou de votre péroné ?",
            "Avez-vous remarqué une bosse ou un gonflement sur votre jambe, entre le genou et la cheville ?",
            "Avez-vous ressenti une douleur ou une sensibilité particulière après un coup ou une chute sur votre jambe ?"
        ]
    elif type == "N01RX085":
        return [
            "Ressentez-vous une douleur au genou qui s’intensifie quand vous montez ou descendez les escaliers ?",
            "Avez-vous l’impression que votre genou se coince ou qu’il manque de stabilité quand vous marchez ?",
            "Avez-vous remarqué que votre genou gonfle, notamment après une activité ou en fin de journée ?"
        ]
    elif type == "N01RX086":
        return [
            "Ressentez-vous une douleur sous le talon ou sous le pied quand vous marchez ou restez debout longtemps ?",
            "Avez-vous remarqué que votre gros orteil ou d’autres orteils se déforment ou se chevauchent ?",
            "Votre pied a-t-il tendance à enfler, surtout en fin de journée ou après une marche prolongée ?"
        ]
    elif type == "Radio du squelette":
        return [
            "Ressentez-vous des douleurs dans plusieurs parties de votre corps, comme si plusieurs os vous faisaient mal ?",
            "Avez-vous déjà eu plusieurs fractures, parfois pour des chocs ou des chutes mineurs ?",
            "Le médecin vous a-t-il parlé d’un problème de croissance ou de solidité de vos os ?"
        ]
    else :
      []


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        query = req_body.get('code_exam')

        if not query:
            return func.HttpResponse(
                json.dumps({"error": "No query provided in request body"}),
                mimetype="application/json",
                status_code=400
            )

        result = get_interro(query)

        return func.HttpResponse(
            json.dumps({"response": result}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
